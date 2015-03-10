# -*- coding: utf-8 -*-


def set_action(actions, name, value):
    val = list(value) if isinstance(value, set) else value
    if val:
        actions[name] = val


def generate_actions(subscription, policy_granted_permissions, wanted_permissions, ignore_grants_and_vetos):
    actions = {}

    current_permissions = set(subscription.get('permissions', []))
    current_grants = set(subscription.get('grants', []))
    current_vetos = set(subscription.get('vetos', []))

    # Wanted permissions non granted by policy
    wanted_permissions_that_need_grant = wanted_permissions - policy_granted_permissions

    # Non wanted permissions granted by policy
    non_wanted_permissions_that_need_veto = (policy_granted_permissions.union(current_grants)) - wanted_permissions

    if subscription:
        # Current existing permissions not provided neither from policy or grant
        invalid_existing_permissions = current_permissions - policy_granted_permissions - current_grants

        # Current missing permissions provided by policy that are not vetoed
        missing_permissions = policy_granted_permissions - current_permissions
        invalid_missing_permissions = missing_permissions - current_vetos

        # On invalid permissions, trigger a reset. The need of grants and revokes
        # Will be calculated from here assuming a reset status with no vetos neither grants
        if invalid_missing_permissions or invalid_existing_permissions:
            actions['reset'] = True
            current_grants = set([])
            current_vetos = set([])
            missing_permissions = set([])  # a reset will grant all policy permissions that are missing

        # We need to grant all wanted permissions that
        # are not granted by the default context policy
        # and that are not already granted
        # Permissions that has been explicitly revoked become granted again here
        permissions_that_need_grant = (wanted_permissions_that_need_grant - current_grants).union(missing_permissions)
        if not ignore_grants_and_vetos:
            permissions_that_need_grant = permissions_that_need_grant - current_vetos
        set_action(actions, 'grant', permissions_that_need_grant)

        # We need to revoke all non-wanted permissions that
        # are granted by the default context policy
        # And are not already revoked
        permissions_that_need_revoke = non_wanted_permissions_that_need_veto - current_vetos
        if not ignore_grants_and_vetos:
            permissions_that_need_revoke = permissions_that_need_revoke - current_grants
        set_action(actions, 'revoke', permissions_that_need_revoke)
    else:
        actions["subscribe"] = True

        # We need to grant all wanted permissions that
        # are not granted by the default context policy
        set_action(actions, 'grant', wanted_permissions_that_need_grant)

        # We need to revoke all non-wanted permissions that
        # are granted by the default context policy
        set_action(actions, 'revoke', non_wanted_permissions_that_need_veto)

    return actions
