# -*- coding: utf-8 -*-
from maxcarrot import RabbitClient
from maxcarrot import RabbitMessage

from max.exceptions import ConnectionError

from persistent.mapping import PersistentMapping
from socket import error as socket_error

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
