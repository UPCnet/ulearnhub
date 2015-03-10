from ulearnhub.models.components import MaxServer
from ulearnhub.models.components import LdapServer
from ulearnhub.models.components import RabbitServer

from ulearnhub.models.utils import generate_actions, set_action

from itertools import chain


class Service(object):

    def __init__(self, domain, request):
        self.domain = domain
        self.request = request
        self.data = request.json

    def run(self):
        for component_name in self.target_components:
            handler = self.get_component_handler(component_name)
            handler()
        return {}

    def get_component_handler(self, component_name):
        return getattr(self, 'handle_{}'.format(component_name))

    def noop(self):
        pass


class SyncACL(Service):
    name = 'syncacl'
    target_components = ['rabbitmq']

    def handle_rabbitmq(self, *args, **kwargs):
        """
            Queues subscription tasks to the domain's rabbitmq broker.

            Format of request as follows:

            {
                "component": {
                    "type": "communities",
                    "id": "url"
                }
                "permission_mapping": {
                    "reader": ['read'],
                    "writer": ['read', 'write'],
                    "owner": ['read', 'write']
                },
                "ignore_grants_and_vetos": true,
                "context": "http://(...)",
                "acl": {
                    "groups": [
                        {"id": , "role": ""},
                        ...
                    ]
                    "users": [
                        {"id": , "role": ""},
                    ]
                }
            }
        """
        # Get required components for this service
        maxserver = self.domain.get_component(MaxServer)
        ldapserver = self.domain.get_component(LdapServer)
        rabbitserver = self.domain.get_component(RabbitServer)

        # Get target context and all of its subscriptions
        maxclient = maxserver.maxclient
        username, token = self.request.auth
        maxclient.setActor(maxserver.user)
        maxclient.setToken(maxserver.token)

        # Collect data and variables needed
        context = maxclient.contexts[self.data['context']].get()
        subscriptions = maxclient.contexts[self.data['context']].subscriptions.get()
        acl_groups = self.data['acl'].get('groups', [])
        acl_users = self.data['acl'].get('users', [])
        permission_mapping = self.data['permission_mapping']

        policy_granted_permissions = set([permission for permission, value in context.get('permissions', {}).items() if value in ['subscribed', 'public']])

        # Prepare a user mapped copy of context subscriptions
        subscriptions_by_user = {}
        for subscription in subscriptions:
            subscriptions_by_user[subscription['username']] = subscription

        # To keep track of overwrites caused by user duplication
        # At the end of the process, subscribed user NOT IN target users
        # will be unsubscribed
        actions_by_user = {}

        def expanded_users():
            """
                Returns iterator with groups in request expanded to get all individual users.

                Transform each user to mimic entries in requests's ['acl']['users'],
                picking the role specified in the group. Preserve group for further checks.

            """
            if not acl_groups:
                raise StopIteration()

            ldapserver.server.connect(userdn=True)
            for group in acl_groups:
                users = ldapserver.server.get_branch_group_users(None, group['id'])
                for username in users:
                    yield {'id': username, 'role': group['role'], 'group': group['id']}

            # Disconnect ldap server, we won't need it outside here
            ldapserver.server.disconnect()

        def merge_actions(old_actions, new_actions):
            actions = {}
            if old_actions is None:
                return new_actions

            if old_actions or new_actions:
                if 'subscribe' in old_actions or 'subscribe' in new_actions:
                    actions['subscribe'] = True

                if 'reset' in old_actions or 'reset' in new_actions:
                    actions['reset'] = True

                if 'grant' in old_actions or 'grant' in new_actions:
                    grants = set(old_actions.get('grant', [])).union(set(new_actions.get('grant', [])))
                    set_action(actions, 'grant', grants)

                if 'revoke' in old_actions or 'revoke' in new_actions:
                    revokes = set(old_actions.get('revoke', [])).intersection(set(new_actions.get('revoke', [])))
                    set_action(actions, 'revoke', revokes)

            return actions

        # Iterate over group users and single users acl's at once
        for user in chain(expanded_users(), acl_users):
            username = user['id']
            role = user['role']

            wanted_permissions = set(permission_mapping.get(role, []))

            # Get the previous defined actions on this user, if any
            actions = actions_by_user.get(username, None)

            # Generate actions based on current permissions, policy, and wanted permissions
            new_actions = generate_actions(
                subscriptions_by_user.get(username, {}),
                policy_granted_permissions,
                wanted_permissions
            )

            # Merge new actions into previous actions, preserving the most beneficient
            actions = merge_actions(actions, new_actions)

            # Store user to track overwrites
            actions_by_user[username] = actions

        # All the users present in subscription and not in the ACL's will be unsubscribed
        missing_users = set(subscriptions_by_user.keys()) - set(actions_by_user.keys())
        for username in missing_users:
            rabbitserver.notifications.sync_acl(context['hash'], username, {"unsubscribe": True})

        for username, actions in actions_by_user.items():
            if actions:
                rabbitserver.notifications.sync_acl(context['hash'], username, actions)

        return {}

SERVICES = {klass.name: klass for klass in locals().values() if Service in getattr(klass, '__bases__', [])}
