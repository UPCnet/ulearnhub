# -*- coding: utf-8 -*-
from maxcarrot import RabbitClient

from ulearnhub.resources import create_defaults
from ulearnhub.tests.mockers.deployments import TEST_VHOST_URL
from ulearnhub.tests import UlearnHUBBaseTestCase
from ulearnhub.tests import test_user
from ulearnhub.tests.mockers.http import http_mock_checktoken
from ulearnhub.tests.mockers.http import http_mock_get_context
from ulearnhub.tests.mockers.http import http_mock_get_context_subscriptions
from ulearnhub.tests.mockers.http import http_mock_info
from ulearnhub.tests.utils import UlearnhubTestApp
from ulearnhub.tests import oauth2Header
from ulearnhub.tests import BASE_DOMAIN

from mock import patch
from paste.deploy import loadapp

import httpretty
import json
import os
import unittest
import time


def ldap_patch_group_search(response):
    def patched(ldapserver, group, *args, **kwargs):
        return response[group]
    return patch('gummanager.libs._ldap.LdapServer.get_group_users', new=patched)


def ldap_patch_connect():
    def patched(*args, **kwargs):
        return True
    return patch('gummanager.libs._ldap.LdapServer.connect', new=patched)


def ldap_patch_disconnect():
    def patched(*args, **kwargs):
        return True
    return patch('gummanager.libs._ldap.LdapServer.disconnect', new=patched)


class UlearnhubSyncaclFunctionalTests(UlearnHUBBaseTestCase):

    def setUp(self):
        conf_dir = os.path.dirname(__file__)
        self.app = loadapp('config:tests.ini', relative_to=conf_dir)

        self.testapp = UlearnhubTestApp(self)

        self.rabbit = RabbitClient(TEST_VHOST_URL)
        self.rabbit.management.cleanup(delete_all=True)
        self.rabbit.declare()

        httpretty.enable()
        http_mock_info()
        http_mock_checktoken()

        create_defaults(self.testapp.testapp.app.registry, BASE_DOMAIN, quiet=True)
        self.initialize_test_deployment()
        self.initialize_test_domain()

        self.patches = []
        self.clients = {}

    def tearDown(self):
        # Make sure httpretty is disabled
        httpretty.disable()
        httpretty.reset()
        for testpatch in self.patches:
            testpatch.stop()

        self.rabbit.get_all('syncacl')

        self.rabbit.disconnect()
        for user_clients in self.clients.values():
            for client in user_clients:
                client.disconnect()

    def assertMessagesInQueue(self, queue, retries=0, expected=None):
        messages = self.rabbit.get_all(queue)
        expected_message_count = expected if expected is not None else len(messages)

        for retry in xrange(retries):
            if len(messages) < expected_message_count:
                messages += self.rabbit.get_all(queue)
            else:
                break

            time.sleep(1)

        if len(messages) < expected_message_count:
            raise AssertionError(
                'Missing messages on queue, expected {}, received {}, retryied {}'.format(
                    expected_message_count,
                    len(messages),
                    retries
                ))
        return {item[0]['u']['u']: item[0] for item in messages}

    def test_domain_syncacl_bad_subscription_permissions(self):
        """
            Given I'm a user without enough subscription permissions on max
            When I try to execute the service
            I get a Forbidden exception
        """
        from .mockers.syncacl import batch_subscribe_request
        from .mockers.syncacl import context as context
        from .mockers.syncacl import initial_subscriptions as subscriptions

        aclless_context = context.copy()
        aclless_context['acls'] = []

        http_mock_get_context(aclless_context)
        http_mock_get_context_subscriptions(subscriptions)

        self.testapp.post('/api/domains/test/services/syncacl'.format(), json.dumps(batch_subscribe_request), headers=oauth2Header(test_user), status=403)

    def test_domain_syncacl_bad_context_permissions(self):
        """
            Given I'm a user without enough context permissions on max
            When I try to execute the service
            I get a Forbidden exception
        """
        from .mockers.syncacl import batch_subscribe_request
        from .mockers.syncacl import context as context
        from .mockers.syncacl import initial_subscriptions as subscriptions

        http_mock_get_context(context, status=403)
        http_mock_get_context_subscriptions(subscriptions)

        self.testapp.post('/api/domains/test/services/syncacl'.format(), json.dumps(batch_subscribe_request), headers=oauth2Header(test_user), status=403)

    def test_domain_syncacl_initial_subscriptions(self):
        """
            Given a newly created context
            When a bunch of users and groups acls are synced
            Then a set of actions is generated to generate needed subscriptions grants and revokes for new subscriptors
        """
        from .mockers.syncacl import batch_subscribe_request
        from .mockers.syncacl import context as context
        from .mockers.syncacl import initial_subscriptions as subscriptions
        from .mockers.syncacl import ldap_test_group, ldap_test_group2, ldap_test_group3

        http_mock_get_context(context)
        http_mock_get_context_subscriptions(subscriptions)

        self.add_patch(ldap_patch_connect())
        self.add_patch(ldap_patch_disconnect())
        self.add_patch(ldap_patch_group_search({
            'TestGroup': ldap_test_group,
            'TestGroup2': ldap_test_group2,
            'TestGroup3': ldap_test_group3
        }))

        self.testapp.post('/api/domains/test/services/syncacl'.format(), json.dumps(batch_subscribe_request), headers=oauth2Header(test_user), status=200)

        # Index by username to be able to make asserts
        # This is mandatory, as we cannot assume the order of the queue
        messages = self.assertMessagesInQueue('syncacl', retries=3, expected=9)

        # Test group users new subscription without grants
        self.assertItemsEqual(messages['groupuser1']['d']['tasks'], ['subscribe'])
        self.assertIn('context', messages['groupuser1']['d'])

        self.assertItemsEqual(messages['groupuser2']['d']['tasks'], ['subscribe'])
        self.assertIn('context', messages['groupuser2']['d'])

        # Test group users new subscription with single grant
        self.assertItemsEqual(messages['groupuser3']['d']['tasks'], ['subscribe', 'grant'])
        self.assertItemsEqual(messages['groupuser3']['d']['tasks']['grant'], ['write'])
        self.assertIn('context', messages['groupuser3']['d'])

        self.assertItemsEqual(messages['groupuser4']['d']['tasks'], ['subscribe', 'grant'])
        self.assertItemsEqual(messages['groupuser4']['d']['tasks']['grant'], ['write'])
        self.assertIn('context', messages['groupuser4']['d'])

        # Test group users new subscription with single revoke
        self.assertItemsEqual(messages['groupuser5']['d']['tasks'], ['subscribe', 'revoke'])
        self.assertItemsEqual(messages['groupuser5']['d']['tasks']['revoke'], ['unsubscribe'])
        self.assertIn('context', messages['groupuser5']['d'])

        self.assertItemsEqual(messages['groupuser6']['d']['tasks'], ['subscribe', 'revoke'])
        self.assertItemsEqual(messages['groupuser6']['d']['tasks']['revoke'], ['unsubscribe'])
        self.assertIn('context', messages['groupuser6']['d'])

        # Test single user new subscription with single grant
        self.assertItemsEqual(messages['testuser1']['d']['tasks'], ['subscribe', 'grant'])
        self.assertItemsEqual(messages['testuser1']['d']['tasks']['grant'], ['write'])
        self.assertIn('context', messages['testuser1']['d'])

        # Test single user new subscription with multiple grant
        self.assertItemsEqual(messages['testowner']['d']['tasks'], ['subscribe', 'grant'])
        self.assertItemsEqual(messages['testowner']['d']['tasks']['grant'], ['write', 'flag'])
        self.assertIn('context', messages['testowner']['d'])

        # Test cretor grant
        self.assertItemsEqual(messages['testuser.creator']['d']['tasks'], ['grant'])
        self.assertItemsEqual(messages['testuser.creator']['d']['tasks']['grant'], ['flag'])
        self.assertIn('context', messages['testuser1']['d'])

    def test_domain_syncacl_change_acls(self):
        """
            Given a existing context with subcriptions
            When a bunch of users and groups acls are synced
            Then a set of actions is generated to update thouse users subscriptions
            And the users that have been removed from acl are unsubscribed
        """
        from .mockers.syncacl import batch_subscribe_request2
        from .mockers.syncacl import context as context
        from .mockers.syncacl import existing_subscriptions as subscriptions
        from .mockers.syncacl import ldap_test_group, ldap_test_group2, ldap_test_group3

        http_mock_get_context(context)
        http_mock_get_context_subscriptions(subscriptions)

        self.add_patch(ldap_patch_connect())
        self.add_patch(ldap_patch_disconnect())
        self.add_patch(ldap_patch_group_search({
            'TestGroup': ldap_test_group,
            'TestGroup2': ldap_test_group2,
            'TestGroup3': ldap_test_group3
        }))

        self.testapp.post('/api/domains/test/services/syncacl'.format(), json.dumps(batch_subscribe_request2), headers=oauth2Header(test_user), status=200)

        # Index by username to be able to make asserts
        # This is mandatory, as we cannot assume the order of the queue
        messages = self.assertMessagesInQueue('syncacl', retries=3, expected=6)

        # Testuser1 remains untouched
        self.assertNotIn('testuser1', messages)

        # Users from gropu 2 remains untouched
        self.assertNotIn('groupuser3', messages)
        self.assertNotIn('groupuser4', messages)

        # Test subscribed group users revoke permission
        self.assertItemsEqual(messages['groupuser1']['d']['tasks'], ['revoke'])
        self.assertItemsEqual(messages['groupuser1']['d']['tasks']['revoke'], ['write'])
        self.assertIn('context', messages['groupuser1']['d'])

        self.assertItemsEqual(messages['groupuser2']['d']['tasks'], ['revoke'])
        self.assertItemsEqual(messages['groupuser2']['d']['tasks']['revoke'], ['write'])
        self.assertIn('context', messages['groupuser2']['d'])

        # Test subscribed group users unsubscribe
        self.assertItemsEqual(messages['groupuser5']['d']['tasks'], ['unsubscribe'])
        self.assertIn('context', messages['groupuser5']['d'])

        self.assertItemsEqual(messages['groupuser6']['d']['tasks'], ['unsubscribe'])
        self.assertIn('context', messages['groupuser6']['d'])

        # Test subscribed single user unsubscribe
        self.assertItemsEqual(messages['testowner']['d']['tasks'], ['unsubscribe'])
        self.assertIn('context', messages['testowner']['d'])

        # Test subscribed user revoke permission
        self.assertItemsEqual(messages['testuser.creator']['d']['tasks'], ['revoke'])
        self.assertItemsEqual(messages['testuser.creator']['d']['tasks']['revoke'], ['flag'])
        self.assertIn('context', messages['testuser.creator']['d'])

    def test_domain_syncacl_user_overwrites_group_permissions(self):
        """
            Given a existing context with subcriptions
            When a bunch of users and groups acls are synced
            And a user from a group acl is also in users acl
            And both group and user has the same role
            Then the same and only action is generated

        """
        from .mockers.syncacl import batch_subscribe_request3
        from .mockers.syncacl import context as context
        from .mockers.syncacl import initial_subscriptions as subscriptions
        from .mockers.syncacl import ldap_test_group4

        http_mock_get_context(context)
        http_mock_get_context_subscriptions(subscriptions)

        self.add_patch(ldap_patch_connect())
        self.add_patch(ldap_patch_disconnect())
        self.add_patch(ldap_patch_group_search({
            'TestGroup4': ldap_test_group4
        }))

        self.testapp.post('/api/domains/test/services/syncacl'.format(), json.dumps(batch_subscribe_request3), headers=oauth2Header(test_user), status=200)

        # Index by username to be able to make asserts
        # This is mandatory, as we cannot assume the order of the queue
        messages = self.assertMessagesInQueue('syncacl', retries=3, expected=2)

        self.assertItemsEqual(messages['groupuser1']['d']['tasks'], ['grant', 'subscribe'])
        self.assertItemsEqual(messages['groupuser1']['d']['tasks']['grant'], ['write', 'flag'])
        self.assertIn('context', messages['groupuser1']['d'])

        # Test subscribed user revoke permission
        self.assertItemsEqual(messages['testuser.creator']['d']['tasks'], ['grant'])
        self.assertItemsEqual(messages['testuser.creator']['d']['tasks']['grant'], ['flag'])
        self.assertIn('context', messages['testuser.creator']['d'])

    def test_domain_syncacl_user_overwrites_user_permissions(self):
        """
            Given a existing context with subcriptions
            When a bunch of users and groups acls are synced
            And a user from a group acl is also in users acl
            And both group and user has the same role
            Then the action with more permissions is preserved

        """
        from .mockers.syncacl import batch_subscribe_request4
        from .mockers.syncacl import context as context
        from .mockers.syncacl import initial_subscriptions as subscriptions

        http_mock_get_context(context)
        http_mock_get_context_subscriptions(subscriptions)

        self.testapp.post('/api/domains/test/services/syncacl'.format(), json.dumps(batch_subscribe_request4), headers=oauth2Header(test_user), status=200)

        # Index by username to be able to make asserts
        # This is mandatory, as we cannot assume the order of the queue
        messages = self.assertMessagesInQueue('syncacl', retries=3, expected=1)

        # Test subscribed user revoke permission, preserves most important role
        self.assertItemsEqual(messages['testuser.creator']['d']['tasks'], ['grant'])
        self.assertItemsEqual(messages['testuser.creator']['d']['tasks']['grant'], ['flag'])
        self.assertIn('context', messages['testuser.creator']['d'])


class UlearnhubSyncaclActionMergingUnitTests(unittest.TestCase):

    def test_merge_empty_with_empty(self):
        """
            Given an empty initial actions set
            And an empty new action set
            When i merge the two sets
            I get an empty action set
        """
        from ulearnhub.models.utils import merge_actions

        actions = merge_actions(None, {})

        self.assertFalse(actions)

    def test_merge_empty_with_subscribe(self):
        """
            Given an empty initial actions set
            And an subscribe new action set
            When i merge the two sets
            I get a copy of the latter
        """
        from ulearnhub.models.utils import merge_actions

        actions = merge_actions(None, {'subscribe': True})

        self.assertItemsEqual(actions, ['subscribe'])

    def test_merge_empty_with_grants(self):
        """
            Given an empty initial actions set
            And a grant new action set
            When i merge the two sets
            I get a copy of the latter
        """
        from ulearnhub.models.utils import merge_actions

        actions = merge_actions(None, {'grant': ['write']})

        self.assertItemsEqual(actions, ['grant'])
        self.assertItemsEqual(actions['grant'], ['write'])

    def test_merge_empty_with_revokes(self):
        """
            Given an empty initial actions set
            And a revoke new action set
            When i merge the two sets
            I get a copy of the latter
        """
        from ulearnhub.models.utils import merge_actions

        actions = merge_actions(None, {'revoke': ['write']})

        self.assertItemsEqual(actions, ['revoke'])
        self.assertItemsEqual(actions['revoke'], ['write'])

    def test_merge_empty_with_all(self):
        """
            Given an empty initial actions set
            And a subscribe + grant + revoke new action set
            When i merge the two sets
            I get a copy of the latter
        """
        from ulearnhub.models.utils import merge_actions

        actions = merge_actions(None, {'revoke': ['write'], 'grant': ['read'], 'subscribe': True})

        self.assertItemsEqual(actions, ['revoke', 'grant', 'subscribe'])
        self.assertItemsEqual(actions['revoke'], ['write'])
        self.assertItemsEqual(actions['grant'], ['read'])

    def test_merge_subscribe_with_empty(self):
        """
            Given an subscribe previous action set
            And an empty new action set
            When i merge the two sets
            I get a copy of the former
        """
        from ulearnhub.models.utils import merge_actions

        actions = merge_actions({'subscribe': True}, {})

        self.assertItemsEqual(actions, ['subscribe'])

    def test_merge_grants_with_empty(self):
        """
            Given a grant previous action set
            And an empty new action set
            When i merge the two sets
            I get a copy of the former
        """
        from ulearnhub.models.utils import merge_actions

        actions = merge_actions({'grant': ['write']}, {})

        self.assertItemsEqual(actions, ['grant'])
        self.assertItemsEqual(actions['grant'], ['write'])

    def test_merge_revokes_with_empty(self):
        """
            Given a revoke previous action set
            And an empty new action set
            When i merge the two sets
            The revokes go away
        """
        from ulearnhub.models.utils import merge_actions

        actions = merge_actions({'revoke': ['write']}, {})

        self.assertItemsEqual(actions, [])

    def test_merge_all_with_empty(self):
        """
            Given a subscribe + grant + revoke previous action set
            And an empty new action set
            When i merge the two sets
            I get a copy of the latter
            And the revokes are gone
        """
        from ulearnhub.models.utils import merge_actions

        actions = merge_actions({'revoke': ['write'], 'grant': ['read'], 'subscribe': True}, {})

        self.assertItemsEqual(actions, ['grant', 'subscribe'])
        self.assertItemsEqual(actions['grant'], ['read'])

    def test_merge_subscribe_multiple_times(self):
        """
            Given a subscribe previous action set
            And an subscribe new action set
            And a third subscribe action set
            When i merge the three sets
            I get a copy also with subscribe set
        """

        from ulearnhub.models.utils import merge_actions

        actions = merge_actions({'subscribe': True}, {'subscribe': True})
        actions = merge_actions(actions, {'subscribe': True})

        self.assertItemsEqual(actions, ['subscribe'])

    def test_merge_grants_multiple_times(self):
        """
            Given a grants previous action set
            And an grant new action set
            And a third grant action set
            When i merge the three sets
            I get a copy with grants union of all sets
            And without duplicated grants
        """

        from ulearnhub.models.utils import merge_actions

        actions = merge_actions({'grant': ['write', 'read']}, {'grant': ['read']})
        actions = merge_actions(actions, {'grant': ['flag']})

        self.assertItemsEqual(actions, ['grant'])
        self.assertItemsEqual(actions['grant'], ['read', 'write', 'flag'])

    def test_merge_revokes_multiple_times(self):
        """
            Given a revoke previous action set
            And an revoke new action set
            And a third revoke action set
            When i merge the three sets
            Then I get a copy with revokes intersection of all sets
            And only revokes present in all sets will remain
        """

        from ulearnhub.models.utils import merge_actions

        actions = merge_actions({'revoke': ['write', 'read']}, {'revoke': ['read']})

        self.assertItemsEqual(actions, ['revoke'])
        self.assertItemsEqual(actions['revoke'], ['read'])

        actions = merge_actions(actions, {'revoke': ['flag']})

        self.assertItemsEqual(actions, [])

    def test_merge_revokes_multiple_times_preserve_grants(self):
        """
            Given a revoke previous action set
            And an revoke new action set
            And a third grant action set
            When I merge the three sets
            Then I get a copy with revokes intersection of all sets
            And I get a copy with grants unions of all sets
            And only revokes also present in grants dissappear
        """

        from ulearnhub.models.utils import merge_actions

        actions = merge_actions({'revoke': ['write', 'read']}, {'revoke': ['read']})
        actions = merge_actions(actions, {'grant': ['read']})

        self.assertItemsEqual(actions, ['grant'])
        self.assertItemsEqual(actions['grant'], ['read'])

    def test_merge_grants_multiple_times_preserve_grants(self):
        """
            Given a grant previous action set
            And an grant new action set
            And a third revoke action set
            When I merge the three sets
            Then I get a copy with revokes intersection of all sets
            And I get a copy with grants unions of all sets
            And revokes from third set won't remove grants
        """

        from ulearnhub.models.utils import merge_actions

        actions = merge_actions(None, {'grant': ['write'], 'revoke': ['read']})
        actions = merge_actions(actions, {'grant': ['read'], 'revoke': ['read']})

        self.assertItemsEqual(actions, ['grant'])
        self.assertItemsEqual(actions['grant'], ['write', 'read'])


class UlearnhubSyncaclActionGenerationUnitTests(unittest.TestCase):

    def test_action_generation_new_subscription(self):
        """
            Given a set of wanted permissions
            And an inexistent subcription
            If all wanted permissions are in policy
            Then only subscription action is generated
        """
        from ulearnhub.models.utils import generate_actions

        subscription = {}
        policy_granted_permissions = set(['write', 'read'])
        wanted_permissions = set(['write', 'read'])

        actions = generate_actions(subscription, policy_granted_permissions, wanted_permissions)

        self.assertItemsEqual(actions.keys(), ['subscribe'])
        self.assertTrue(actions['subscribe'])

    def test_action_generation_new_subscription_triggers_grant(self):
        """
            Given a set of wanted permissions
            And an inexistent subcription
            If there are some wanted permissions not in policy
            Then a subscription action is generated
            And a grant action is generated
        """
        from ulearnhub.models.utils import generate_actions

        subscription = {}
        policy_granted_permissions = set(['read'])
        wanted_permissions = set(['write', 'read'])

        actions = generate_actions(subscription, policy_granted_permissions, wanted_permissions)

        self.assertItemsEqual(actions.keys(), ['subscribe', 'grant'])
        self.assertTrue(actions['subscribe'])
        self.assertItemsEqual(actions['grant'], ['write'])

    def test_action_generation_new_subscription_triggers_revoke(self):
        """
            Given a set of wanted permissions
            And an inexistent subcription
            If there are some not wanted permissions in policy
            Then a subscription action is generated
            And a revoke action is generated
        """
        from ulearnhub.models.utils import generate_actions

        subscription = {}
        policy_granted_permissions = set(['read', 'write'])
        wanted_permissions = set(['read'])

        actions = generate_actions(subscription, policy_granted_permissions, wanted_permissions)

        self.assertItemsEqual(actions.keys(), ['subscribe', 'revoke'])
        self.assertTrue(actions['subscribe'])
        self.assertItemsEqual(actions['revoke'], ['write'])

    def test_action_generation_new_subscription_triggers_grant_and_revoke(self):
        """
            Given a set of wanted permissions
            And an inexistent subcription
            If there are some wanted permissions not in policy
            If there are some not wanted permissions in policy
            Then a subscription action is generated
            And a revoke action is generated
            And a grant action is generated
        """
        from ulearnhub.models.utils import generate_actions

        subscription = {}
        policy_granted_permissions = set(['write'])
        wanted_permissions = set(['read'])

        actions = generate_actions(subscription, policy_granted_permissions, wanted_permissions)

        self.assertItemsEqual(actions.keys(), ['subscribe', 'revoke', 'grant'])
        self.assertTrue(actions['subscribe'])
        self.assertItemsEqual(actions['revoke'], ['write'])
        self.assertItemsEqual(actions['grant'], ['read'])

# ACTIONS OVER EXISTING SUBSCRIPTIONS

    def test_action_generation_subscribed(self):
        """
            Given a set of wanted permissions
            And an existent subcription
            If we currently have all wanted permissions
            Then no action is generated
        """
        from ulearnhub.models.utils import generate_actions

        subscription = {'permissions': ['read', 'write']}
        policy_granted_permissions = set(['read', 'write'])
        wanted_permissions = set(['read', 'write'])

        actions = generate_actions(subscription, policy_granted_permissions, wanted_permissions)

        self.assertItemsEqual(actions.keys(), [])

    def test_action_generation_subscribed_triggers_grant(self):
        """
            Given a set of wanted permissions
            And an existent subcription
            If there are some wanted permissions that we don't have
            Then a grant action is generated
        """
        from ulearnhub.models.utils import generate_actions

        subscription = {'permissions': ['read']}
        policy_granted_permissions = set(['read'])
        wanted_permissions = set(['read', 'write'])

        actions = generate_actions(subscription, policy_granted_permissions, wanted_permissions)

        self.assertItemsEqual(actions.keys(), ['grant'])
        self.assertItemsEqual(actions['grant'], ['write'])

    def test_action_generation_subscribed_triggers_revoke(self):
        """
            Given a set of wanted permissions
            And an existent subcription
            If we have some permissions that we must not have
            And that permissions has been granted
            Then a revoke action is generated
        """
        from ulearnhub.models.utils import generate_actions

        subscription = {'permissions': ['read', 'write']}
        policy_granted_permissions = set(['read', 'write'])
        wanted_permissions = set(['read'])

        actions = generate_actions(subscription, policy_granted_permissions, wanted_permissions)

        self.assertItemsEqual(actions.keys(), ['revoke'])
        self.assertItemsEqual(actions['revoke'], ['write'])

    def test_action_generation_subscribed_triggers_revoke_and_grant(self):
        """
            Given a set of wanted permissions
            And an existent subcription
            If there are some wanted permissions not in current permissions
            If there are some not wanted permissions in current_permissions
            Then a subscription action is generated
            And a revoke action is generated
            And a grant action is generated
        """
        from ulearnhub.models.utils import generate_actions

        subscription = {'permissions': ['read', 'write']}
        policy_granted_permissions = set(['write'])
        wanted_permissions = set(['read', 'flag'])

        actions = generate_actions(subscription, policy_granted_permissions, wanted_permissions)

        self.assertItemsEqual(actions.keys(), ['revoke', 'grant'])
        self.assertItemsEqual(actions['revoke'], ['write'])
        self.assertItemsEqual(actions['grant'], ['flag'])
