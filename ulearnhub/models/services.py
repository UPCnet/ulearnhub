from ulearnhub.models.components import MaxServer
from ulearnhub.models.components import LdapServer
from ulearnhub.models.components import RabbitServer

from ulearnhub.models.utils import generate_actions
from ulearnhub.models.utils import merge_actions

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
        authenticated_username, authenticated_token = self.request.auth
        maxclient.setActor(authenticated_username)
        maxclient.setToken(authenticated_token)

        # Collect data and variables needed
        context = maxclient.contexts[self.data['context']].get(qs=dict(show_acls=True))
        subscriptions = maxclient.contexts[self.data['context']].subscriptions.get(qs={'limit': 0})
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
            rabbitserver.notifications.sync_acl(self.domain.name, context['url'], username, {"unsubscribe": True})

        for username, actions in actions_by_user.items():
            if actions:
                rabbitserver.notifications.sync_acl(self.domain.name, context['url'], username, actions)

        return {}

SERVICES = {klass.name: klass for klass in locals().values() if Service in getattr(klass, '__bases__', [])}
