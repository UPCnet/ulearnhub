# -*- coding: utf-8 -*-


def set_action(actions, name, value):
    val = list(value) if isinstance(value, set) else value
    if val:
        actions[name] = val


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
