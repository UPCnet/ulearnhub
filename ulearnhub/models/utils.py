# -*- coding: utf-8 -*-


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
