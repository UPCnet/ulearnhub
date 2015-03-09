from ulearnhub.models.components import MaxServer
from ulearnhub.models.components import LdapServer
from ulearnhub.models.components import RabbitServer

from ulearnhub.models.utils import generate_actions

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
        maxclient.setActor(username)
        maxclient.setToken(token)

        context = maxclient.contexts[self.data['context']].get()
        subscriptions = maxclient.contexts[self.data['context']].subscriptions.get()

        permissions = set(['write', 'read', 'subscribe', 'unsubscribe', 'invite', 'delete', 'flag'])
        policy_granted_permissions = set([permission for permission in permissions if context.get('permissions', {}).get(permission, 'restricted') in ['subscribed', 'public']])

        # Prepare a user mapped copy of context subscriptions
        subscriptions_by_user = {}
        for subscription in subscriptions:
            subscriptions_by_user[subscription['username']] = subscription

        # To keep track of overwrites caused by user duplication
        # At the end of the process, subscribed user NOT IN target users
        # will be unsubscribed
        target_users = {}
        overwrites = {}

        def expanded_users():
            """
                Returns iterator with groups in request expanded to get all individual users.

                Transform each user to mimic entries in requests's ['acl']['users'],
                picking the role specified in the group. Preserve group for further checks.

            """
            ldapserver.server.connect(userdn=True)
            for group in self.data['acl']['groups']:
                users = ldapserver.server.get_branch_group_users(None, group['id'])
                for username in users:
                    yield {'id': username, 'role': group['role'], 'group': group['id']}

        # Generate an action list per-user that must be performed in the right order (groups, users)
        # to ensuer leaving each user with the required permission set. Users defined twice
        # will be overwritten by the last occurrence. Individual users preceed group users.

        for user in chain(expanded_users(), self.data['acl']['users']):
            username = user['id']
            role = user['role']
            source = user.get('group', 'users')
            wanted_permissions = set(self.data['permission_mapping'].get(role))

            # Log permission overwrites that may happen during assignment
            if username in target_users:
                overwrites['username'] = {
                    'old': target_users[username]['source'],
                    'new': source}

            # Generate actions based on current permissions, policy, and wanted permissions
            actions = generate_actions(
                subscriptions_by_user.get(username, {}),
                policy_granted_permissions,
                wanted_permissions)

            # Only send actions if there's something to do...
            if actions:
                rabbitserver.notifications.sync_acl(username, actions)

            # Store user to track overwrites
            target_users[username] = {"source": source}

        # Disconnect ldap server, we won't need it again
        ldapserver.server.disconnect()

        # All the users present in subscription and not in the ACL's will be unsubscribed
        missing_users = set(subscriptions_by_user.keys()) - set(target_users.keys())
        for username in missing_users:
            rabbitserver.notifications.sync_acl(username, {"unsubscribe": True})

        return {}

SERVICES = {klass.name: klass for klass in locals().values() if Service in getattr(klass, '__bases__', [])}
