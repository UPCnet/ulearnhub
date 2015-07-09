# -*- coding: utf-8 -*-
from maxcarrot import RabbitClient
from maxcarrot import RabbitMessage

from max.exceptions import ConnectionError

from persistent.mapping import PersistentMapping
from socket import error as socket_error
from max.security import permissions as max_permissions
from max.exceptions import Forbidden
from maxclient.client import RequestError
import json
import pkg_resources
import sys


class ConfigWrapper(PersistentMapping):

    @classmethod
    def from_dict(cls, config):
        wrapper = cls()

        def wrap(wvalue):
            if isinstance(wvalue, dict):
                return ConfigWrapper.from_dict(wvalue)
            elif isinstance(wvalue, list):
                wrapped_list = []
                for item in wvalue:
                    wrapped_list.append(wrap(item))
                return wrapped_list
            else:
                return wvalue

        for key, value in config.items():
            wrapped = wrap(value)
            wrapper[key] = wrapped

        return wrapper

    def __getattr__(self, key):
        if key in self:
            return self[key]

        else:
            raise AttributeError(key)


def noop(*args, **kwargs):
    """
        Dummy method executed in replacement of the requested method
        when rabbitmq is not defined (i.e. in tests)
    """
    pass


class RabbitNotifications(object):
    """
        Wrapper to access notification methods, and catch possible exceptions
    """

    def __init__(self, url):
        self.url = url
        self.message_defaults = {
            "source": "hub",
            "version": pkg_resources.require("ulearnhub")[0].version,
        }

        client_properties = {
            "product": "hub",
            "version": pkg_resources.require("ulearnhub")[0].version,
            "platform": 'Python {0.major}.{0.minor}.{0.micro}'.format(sys.version_info),
        }
        self.enabled = True

        try:
            self.client = RabbitClient(self.url, client_properties=client_properties, transport='gevent')
        except AttributeError:
            self.enabled = False
        except socket_error:
            raise ConnectionError("Could not connect to rabbitmq broker")

    def sync_acl(self, domain, context, username, tasks):
        """
            Sends a Carrot (TM) notification of a new sync acl task
        """
        # Send a conversation creation notification to rabbit
        message = RabbitMessage()
        message.prepare(self.message_defaults)
        message.update({
            "user": {
                'username': username,
            },
            "domain": domain,
            "action": "modify",
            "object": "context",
            "data": {'context': context,
                     'tasks': tasks}
        })
        self.client.send(
            'syncacl',
            json.dumps(message.packed),
            routing_key='')


def set_action(actions, name, value):
    """
        Sets an action value only if has value.

        Converts set values into lists.
    """
    val = list(value) if isinstance(value, set) else value
    if val:
        actions[name] = val


def merge_actions(old_actions, new_actions):
    """
        Merge two sets of actions.

        Keys will only be added to resulting set if present if one of the two.
        Grants and revoked are processed to preserve the most powerfull permissions.
        So different sets of grants will be mixed togehters, and different sets of
        revokes will be intersected, so only revokes on all actions are preserved.
    """
    actions = {}
    if old_actions is None:
        return new_actions

    if old_actions or new_actions:
        if 'subscribe' in old_actions or 'subscribe' in new_actions:
            actions['subscribe'] = True

        grants = set()
        if 'grant' in old_actions or 'grant' in new_actions:
            grants = set(old_actions.get('grant', [])).union(set(new_actions.get('grant', [])))
            set_action(actions, 'grant', grants)

        if 'revoke' in old_actions or 'revoke' in new_actions:
            revokes = set(old_actions.get('revoke', [])).intersection(set(new_actions.get('revoke', [])))
            # If we have a grant that is also in revokes, remove it from revokes
            set_action(actions, 'revoke', revokes - grants)

    return actions


def generate_actions(subscription, policy_granted_permissions, requested_permissions):
    """
        Generates needed actions to achieve wanted_permissions, ensuring the minimum set of
        actions is performed. Actions here defined will be executed in a non-permanent way, ignoring
        vetos and grants.

    """
    actions = {}

    # If the user is subscribed, the permission set to calculate
    # revokes and grants is the current permission set
    if subscription:
        current_permissions = set(subscription.get('permissions', []))
    # ohterwise, assume the permissions that the user will have
    # oonce subscribed are the ones in the context's policy
    else:
        actions["subscribe"] = True
        current_permissions = policy_granted_permissions

    # Permissions that the user don't have and needs
    missing_permissions = requested_permissions - current_permissions
    set_action(actions, 'grant', missing_permissions)

    # Permissions that the user has and don't needs
    exceeded_permissions = current_permissions - requested_permissions
    set_action(actions, 'revoke', exceeded_permissions)

    return actions


def get_context_data(maxclient, context_url):
    # Collect data and variables needed
    try:
        context = maxclient.contexts[context_url].get(qs=dict(show_acls=True))
    except RequestError as exc:
        if exc.code == 403:
            raise Forbidden('User {} has not enough permissions on max to use this service'.format(
                maxclient.actor['username'])
            )
        else:
            raise exc

    # Check if authenticated user meets the permissions on max to execute the service
    can_execute_service = max_permissions.remove_subscription in context['acls'] \
        and max_permissions.add_subscription in context['acls'] \
        and max_permissions.manage_subcription_permissions in context['acls']

    if not can_execute_service:
        raise Forbidden('User {} has not enough permissions on max to use this service'.format(
            maxclient.actor['username'])
        )

    subscriptions = maxclient.contexts[context_url].subscriptions.get(qs={'limit': 0})
    policy_granted_permissions = set([permission for permission, value in context.get('permissions', {}).items() if value in ['subscribed', 'public']])

    # Prepare a user mapped copy of context subscriptions
    subscriptions_by_user = {}
    for subscription in subscriptions:
        subscriptions_by_user[subscription['username']] = subscription

    return policy_granted_permissions, subscriptions_by_user


def intersect_users(ldap_users, community_groups_users, community_users, context_users):
    """
        Determines which users must be subscribed/unsubscribed by looking at all
        involver user sets:

        ldap_users: List of all users that currently are members of working group
        community_groups_users: Combined list of all users of all groups that are assigned to a community
        community_users: List of all users that are assigned individually to a community
        context_users: List of all users that are currently subscribed to the community max context

        As the list of users to be subscribed is straightforward (simple difference between ldap and
        max users), to calculate the ones to be unsubscribed we have to do a little more things:

        A user that has been removed from a ldap group and is present on max context users, would seem
        that is a candidate to be unsubscribed, but we have to take into account that this user MAY have
        been subscribed individually or by membership of another group. All users matching that rule,
        MUST NOT be unsubscribed.

        More details on set operations to achieve the results in inline comments below.
    """
    # Convert user lists to sets
    current_ldap_group_users = set(ldap_users)
    context_subscribed_users = set(context_users)
    community_assigned_users = set(community_users)
    community_assigned_groups_users = set(community_groups_users)

    # List of all users present in ldap group that are not currently subscribed on max
    users_to_be_subscribed = current_ldap_group_users - context_subscribed_users

    # List of all users NOT in ldap group, that ARE currently subscribed
    potencially_users_to_be_unsubscribed = context_subscribed_users - current_ldap_group_users
    # Users that cannot be unsubscribed, beacause they are subscribed individually
    # OR they are subscribed via another group.
    unsubscribable_users = community_assigned_users.union(community_assigned_groups_users)
    # Final list of users that MUST be unsubscribed
    users_to_be_unsubscribed = potencially_users_to_be_unsubscribed - unsubscribable_users

    return users_to_be_subscribed, users_to_be_unsubscribed


class GroupUsersRetriever(object):
    def __init__(self, ldapserver):
        self.ldap = ldapserver
        self.users_by_group = {}

    def _get_group_users(self, group):
        if group not in self.users_by_group:
            self.users_by_group[group] = self.ldap.server.get_group_users(group)
        return self.users_by_group[group]

    def load(self, *groups):
        users = []
        for group in groups:
            users += self._get_group_users(group)
        return users


