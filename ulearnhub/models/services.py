# -*- coding: utf-8 -*-
from ulearnhub.models.components import LdapServer
from ulearnhub.models.components import MaxServer
from ulearnhub.models.components import RabbitServer
from ulearnhub.models.components import ULearnCommunities
from ulearnhub.models.domains import Domain
from ulearnhub.models.utils import generate_actions
from ulearnhub.models.utils import merge_actions, get_context_data
from ulearnhub.models.utils import GroupUsersRetriever
from ulearnhub.models.utils import intersect_users
from ulearnhub.resources import root_factory
from itertools import chain
import gevent


class ServicesContainer(object):

    def __init__(self, parent):
        self.__parent__ = parent

    def __getitem__(self, key):
        Service = SERVICES[key]
        if isinstance(self.__parent__, Service.allowed_caller):
            return Service(self.__parent__)


class Service(object):

    @property
    def __acl__(self):
        return []

    def __init__(self, parent):
        """
            Store the object that the service is called on.
        """
        self.__parent__ = parent

    def run(self, request):
        for component_name in self.target_components:
            handler = self.get_component_handler(component_name)
            handler(request)
        return {}

    def get_component_handler(self, component_name):
        return getattr(self, 'handle_{}'.format(component_name))

    def noop(self):
        pass


class SyncLDAPGroup(Service):
    name = 'syncldapgroup'
    target_components = ['rabbitmq']
    allowed_caller = LdapServer

    def handle_rabbitmq(self, request, *args, **kwargs):
        """
            Update a groups user subscription on directory changes.

            For any community found using the group contained in the
            request, the full list of users is extracted and a minimum
            set of taskjs (SUB or UNSUB) is generated per-context. At the
            end, any added or removed user in the group will be synced so
            the subscriptions of that context match the users on the group.

            Format of request to this service is as follows:

            {
                "component": {
                    "type": "ldap",
                    "id": ""
                }
                "group": "cn=groupname,dc.....",
                "ignore_grants_and_vetos": true,
            }

        """
        data = request.json
        target_group = data['group']
        ldapserver = self.__parent__

        group_users = GroupUsersRetriever(ldapserver)

        # Expand users
        ldapserver.server.connect()
        ldap_group_current_users = group_users.load(target_group)

        # Disconnect ldap server, we won't need it outside here
        ldapserver.server.disconnect()

        # Search all domains that are using this **exact**
        # component instance
        domains = root_factory(request)['domains']
        target_domains = []
        for domain in domains.values():
            candidate = domain.get_component(ldapserver.__class__)
            if candidate is not None and candidate is ldapserver:
                target_domains.append(domain)

        processed_communities = []
        for domain in target_domains:
            # Get required components to process this domain
            rabbitserver = domain.get_component(RabbitServer)
            communities_site = domain.get_component(ULearnCommunities)
            maxserver = domain.get_component(MaxServer)
            maxclient = maxserver.maxclient
            authenticated_username, authenticated_token, scope = request.auth_headers
            maxclient.setActor(authenticated_username)
            maxclient.setToken(authenticated_token)

            if communities_site in processed_communities:
                continue

            # Get all communities that have the target group assigned
            # on any created_community
            target_communities = communities_site.get_communities_with_group(target_group)
            for context_data in target_communities:
                context_url = context_data['url']
                policy_granted_permissions, max_subscriptions = get_context_data(maxclient, context_url)

                community_assigned_users = context_data['users']
                community_assigned_groups = context_data['groups']
                community_assigned_groups_users = group_users.load(*community_assigned_groups)
                context_subscribed_users = max_subscriptions.keys()

                subscriptions, unsubscriptions = intersect_users(
                    ldap_group_current_users,
                    community_assigned_groups_users,
                    community_assigned_users,
                    context_subscribed_users
                )

                # Generate and queue subcribe/unsubscribe actions
                client = rabbitserver.notifications

                for username in subscriptions:
                    client.sync_acl(domain.name, context_url, username, {"subscribe": True})
                    gevent.sleep()

                for username in unsubscriptions:
                    client.sync_acl(domain.name, context_url, username, {"unsubscribe": True})
                    gevent.sleep()

                gevent.sleep(0.1)

        processed_communities.append(communities_site)
        return {}


class SyncACL(Service):
    name = 'syncacl'
    target_components = ['rabbitmq']
    allowed_caller = Domain

    def handle_rabbitmq(self, request, *args, **kwargs):
        """
            Update a context's users ACLS

            Decomposes given groups into a list of users. With that list of
            users generates the minimum set of tasks (SUB, UNSUB, REVOKE, GRANT)
            to sync the community status to max context and subscriptions.

            Each of the final tasks generated is feeded to rabbitmq
            to be processed asynchronously.

            Format of request to this service is as follows:

            {
                "component": {
                    "type": "communities",
                    "id": "url"
                }
                "context": "http://(...)",
                "acl": {
                    "groups": [
                        {"id": , "role": ""},
                        ...
                    ]
                    "users": [
                        {"id": , "role": ""},
                    ]
                },
                "permission_mapping": {
                    "reader": ['read'],
                    "writer": ['read', 'write'],
                    "owner": ['read', 'write']
                },
                "ignore_grants_and_vetos": true,

            }

            component: type and id of the component that's triggering this call
            context: The context on which the syncacl tasks will be performed
            acl.groups: list of group acls to process.
            acl.users: list of user acls to process.
            acl.*:  Each acl entry has an id identifing the group/user (cn) and a role
            permission_mapping: For each role in acls, there must be a list of permissions that
                a user with that role must have in its max subscription
            ignore_grants_and_vetos: if true, peristent grants and vetoes on context subscriptions
            will be overriden so that the final subscription state matches the requested state. This is
            the default behaviour.
        """

        data = request.json
        domain = self.__parent__
        context_url = data['context']

        # Get required components for this service
        maxserver = domain.get_component(MaxServer)
        ldapserver = domain.get_component(LdapServer)
        rabbitserver = domain.get_component(RabbitServer)

        # Get target context and all of its subscriptions
        maxclient = maxserver.maxclient
        authenticated_username, authenticated_token, scope = request.auth_headers
        maxclient.setActor(authenticated_username)
        maxclient.setToken(authenticated_token)

        policy_granted_permissions, subscriptions = get_context_data(maxclient, context_url)

        acl_groups = data['acl'].get('groups', [])
        acl_users = data['acl'].get('users', [])
        permission_mapping = data['permission_mapping']

        def expanded_users():
            """
                Returns iterator with groups in request expanded to get all individual users.

                Transform each user to mimic entries in requests's ['acl']['users'],
                picking the role specified in the group. Preserve group for further checks.

            """
            if not acl_groups:
                raise StopIteration()

            ldapserver.server.connect()
            for group in acl_groups:
                users = ldapserver.server.get_group_users(group['id'].encode('utf-8'))
                for username in users:
                    yield {'id': username, 'role': group['role'], 'group': group['id']}

            # Disconnect ldap server, we won't need it outside here
            ldapserver.server.disconnect()

        # To keep track of overwrites caused by user duplication
        # At the end of the process, subscribed user NOT IN target users
        # will be unsubscribed
        actions_by_user = {}

        # Iterate over group users and single users acl's at once
        for user in chain(expanded_users(), acl_users):
            username = user['id']
            role = user['role']

            wanted_permissions = set(permission_mapping.get(role, []))

            # Get the previous defined actions on this user, if any
            actions = actions_by_user.get(username, None)

            # Generate actions based on current permissions, policy, and wanted permissions
            new_actions = generate_actions(
                subscriptions.get(username, {}),
                policy_granted_permissions,
                wanted_permissions
            )

            # Merge new actions into previous actions, preserving the most beneficient
            actions = merge_actions(actions, new_actions)

            # Store user to track overwrites
            actions_by_user[username] = actions

        client = rabbitserver.notifications

        # All the users present in subscription and not in the ACL's will be unsubscribed
        missing_users = set(subscriptions.keys()) - set(actions_by_user.keys())
        for username in missing_users:
            client.sync_acl(domain.name, context_url, username, {"unsubscribe": True})
            gevent.sleep()

        for username, actions in actions_by_user.items():
            if actions:
                client.sync_acl(domain.name, context_url, username, actions)
                gevent.sleep()

        gevent.sleep(0.1)
        return {}

SERVICES = {klass.name: klass for klass in locals().values() if Service in getattr(klass, '__bases__', [])}
