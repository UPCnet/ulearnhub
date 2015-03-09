from ulearnhub.models.components import MaxServer
from ulearnhub.models.components import LdapServer

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


class BatchSubscriber(Service):
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

        # Get target context and all of its subscriptions
        maxclient = maxserver.maxclient
        username, token = self.request.auth
        maxclient.setActor(username)
        maxclient.setToken(token)

        context = maxclient.contexts[self.data['context']].get()
        subscriptions = maxclient.contexts[self.data['context']].subscriptions.get()

        # Prepare a user mapped copy of context subscriptions
        subscriptions_by_user = {}
        for subscription in subscriptions:
            subscriptions_by_user[subscription['username']] = subscription

        target_users = {}
        overwrites = {}

        def expanded_users():
            """
                Expand groups in request to get all individual users
                Transform each user to mimic entries in requests's ['acl']['users']
                Picking the role specified in the group. Preserve group for further checks
            """
            ldapserver.server.connect(userdn=True)
            for group in self.data['acl']['groups']:
                users = ldapserver.server.get_branch_group_users(None, group['id'])
                for username in users:
                    yield {'id': username, 'role': group['role'], 'group': group['id']}

        # Generate a list actions per-user that must be performed in order
        # of leaving each user with the required permission set. Users defined twice
        # will be overwritten by the last occurrence. Individual users preceed group users.

        for user in chain(expanded_users(), self.data['acl']['users']):
            username = user['id']
            role = user['role']
            source = user.get('group', 'users')
            wanted_permissions = self.data['permission_mapping'].get(role)

            # Log permission overrwrites that may happen during assignment
            if username in target_users:
                overwrites['username'] = {
                    'old': target_users[username]['source'],
                    'new': source}

            # Set default actions
            is_subscribed = username in subscriptions_by_user
            actions = {
                'subscribe': not is_subscribed,
                'unsubscribe': False,
                'reset': [],
                'grant': [],
                'revoke': [],

            }

            for permission in wanted_permissions:
                # Permission granted if policy is subscribed or public
                permission_granted_by_policy = context.get('permissions', {}).get(permission, 'restricted') in ['subscribed', 'public']

                # Grant permission
                if not is_subscribed and not permission_granted_by_policy:
                    actions['grant'].append(permission)

                if is_subscribed:
                    current_subscription = subscriptions_by_user[username]
                    has_permission = permission in current_subscription['permission']
                    has_grant = permission in current_subscription['grants']
                    has_revoke = permission in current_subscription['revokes']

                    is_clean_permission = not has_grant and not has_revoke

                    # Reset context permissions
                    if permission_granted_by_policy != has_permission and is_clean_permission:
                        actions['reset'].append(permission)

            # Review permission actions if a reset has been triggered
            # Search for permissions NOT RESETTED, that the user MUST HAVE
            # and that are NOT GRANTED by the subscription
            if actions['reset']:
                for permission in wanted_permissions:
                    permission_granted_by_policy = context.get('permissions', {}).get(permission, 'restricted') in ['subscribed', 'public']
                    if permission not in actions['reset'] and not permission_granted_by_policy():
                        actions['grant'].append(permission)

            target_user = {
                "actions": actions,
                "source": source,
            }

            target_users[username] = target_user


        import ipdb;ipdb.set_trace()

        # Disconnect ldap server, we won't need it again
        ldapserver.server.disconnect()
        return {}


SERVICES = {
    'batchsubscriber': BatchSubscriber
}
