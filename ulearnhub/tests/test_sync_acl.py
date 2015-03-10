# -*- coding: utf-8 -*-
from paste.deploy import loadapp
from ulearnhub.tests import test_user
from ulearnhub.tests.utils import oauth2Header
from ulearnhub.tests.utils import UlearnhubTestApp

from ulearnhub.tests.mock_http import http_mock_checktoken
from ulearnhub.tests.mock_http import http_mock_info
from ulearnhub.tests.mock_http import http_mock_get_context
from ulearnhub.tests.mock_http import http_mock_get_context_subscriptions

from maxcarrot import RabbitClient


import httpretty
import json
import os
import unittest
from pyramid.request import Request
from mock import patch
import transaction

RABBIT_URL = "amqp://guest:guest@localhost:5672"
TEST_VHOST_URL = '{}/tests'.format(RABBIT_URL)
RABBIT_MANAGEMENT_URL = "http://localhost:15672/api".format(RABBIT_URL)


def ldap_patch_group_search(response):
    def patched(ldapserver, branch, group, *args, **kwargs):
        return response[group]
    return patch('gummanager.libs._ldap.LdapServer.get_branch_group_users', new=patched)


def ldap_patch_connect():
    def patched(*args, **kwargs):
        return True
    return patch('gummanager.libs._ldap.LdapServer.connect', new=patched)


def ldap_patch_disconnect():
    def patched(*args, **kwargs):
        return True
    return patch('gummanager.libs._ldap.LdapServer.disconnect', new=patched)


class FakeRequest(Request):
    def __init__(self, registry):
        self.registry = registry


class UlearnhubSyncaclFunctionalTests(unittest.TestCase):

    def setUp(self):
        conf_dir = os.path.dirname(__file__)
        self.app = loadapp('config:tests.ini', relative_to=conf_dir)

        self.testapp = UlearnhubTestApp(self)
        self.initialize_zodb()
        self.patches = []

        self.rabbit = RabbitClient(TEST_VHOST_URL)
        self.rabbit.management.cleanup(delete_all=True)
        self.rabbit.declare()

        httpretty.enable()
        http_mock_checktoken()

        self.clients = {}

    def tearDown(self):
        # Make sure httpretty is disabled
        httpretty.disable()
        httpretty.reset()
        for testpatch in self.patches:
            testpatch.stop()

        self.rabbit.disconnect()
        for user_clients in self.clients.values():
            for client in user_clients:
                client.disconnect()

    def add_patch(self, testpatch):
        self.patches.append(testpatch)
        testpatch.start()

    def initialize_zodb(self):
        from ulearnhub import root_factory
        from ulearnhub.models.deployments import Deployments, Deployment
        from ulearnhub.models.domains import Domains, Domain
        from ulearnhub.models.components import MaxCluster, MaxServer, LdapServer, RabbitServer
        request = FakeRequest(self.testapp.testapp.app.registry)
        root = root_factory(request)

        deployments = root['deployments'] = Deployments()
        deployment = deployments['test'] = Deployment(name='test', title='Test Deployment')

        maxcluster = MaxCluster('Test Max Cluster')
        maxserver = MaxServer('Test Max Server', url='http://localhost:8081', user='restricted', token='fw98nyf294')
        ldapserver = LdapServer('LDAP UPC', readonly=True, config={"server": "testldap", "port": 636})
        rabbitserver = RabbitServer('Rabbit UPC', url=TEST_VHOST_URL)

        maxcluster.components.append(maxserver)
        deployment.components.append(maxcluster)
        deployment.components.append(ldapserver)
        deployment.components.append(rabbitserver)

        domains = root['domains'] = Domains()

        test_domain = domains['test'] = Domain(name='test', title='Test Domain')
        test_domain.components.append(ldapserver)
        test_domain.components.append(maxserver)
        test_domain.components.append(rabbitserver)
        transaction.commit()

    def test_domain_syncacl_initial_subscriptions(self):
        """
            Given a newly created context
            When a bunch of users and groups acls are synced
            Then a set of actions is generated to generate needed subscriptions grants and revokes for new subscriptors
        """
        from .mockers import batch_subscribe_request
        from .mockers import context as context
        from .mockers import initial_subscriptions as subscriptions
        from .mockers import ldap_test_group, ldap_test_group2, ldap_test_group3

        http_mock_info()
        http_mock_get_context(context)
        http_mock_get_context_subscriptions(subscriptions)

        self.add_patch(ldap_patch_connect())
        self.add_patch(ldap_patch_disconnect())
        self.add_patch(ldap_patch_group_search({
            'TestGroup': ldap_test_group,
            'TestGroup2': ldap_test_group2,
            'TestGroup3': ldap_test_group3
        }))

        self.testapp.post('/api/domains/test/services/syncacl'.format(), json.dumps(batch_subscribe_request), oauth2Header(test_user), status=200)

        # Index by username to be able to make asserts
        # This is mandatory, as we cannot assume the order of the queue
        messages = self.rabbit.get_all('syncacl')
        messages = {item[0]['u']['u']: item[0] for item in messages}

        self.assertEqual(len(messages), 9)

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
        from .mockers import batch_subscribe_request2
        from .mockers import context as context
        from .mockers import existing_subscriptions as subscriptions
        from .mockers import ldap_test_group, ldap_test_group2, ldap_test_group3

        http_mock_info()
        http_mock_get_context(context)
        http_mock_get_context_subscriptions(subscriptions)

        self.add_patch(ldap_patch_connect())
        self.add_patch(ldap_patch_disconnect())
        self.add_patch(ldap_patch_group_search({
            'TestGroup': ldap_test_group,
            'TestGroup2': ldap_test_group2,
            'TestGroup3': ldap_test_group3
        }))

        self.testapp.post('/api/domains/test/services/syncacl'.format(), json.dumps(batch_subscribe_request2), oauth2Header(test_user), status=200)

        # Index by username to be able to make asserts
        # This is mandatory, as we cannot assume the order of the queue
        messages = self.rabbit.get_all('syncacl')
        messages = {item[0]['u']['u']: item[0] for item in messages}

        self.assertEqual(len(messages), 6)

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
        from .mockers import batch_subscribe_request3
        from .mockers import context as context
        from .mockers import initial_subscriptions as subscriptions
        from .mockers import ldap_test_group4

        http_mock_info()
        http_mock_get_context(context)
        http_mock_get_context_subscriptions(subscriptions)

        self.add_patch(ldap_patch_connect())
        self.add_patch(ldap_patch_disconnect())
        self.add_patch(ldap_patch_group_search({
            'TestGroup4': ldap_test_group4
        }))

        self.testapp.post('/api/domains/test/services/syncacl'.format(), json.dumps(batch_subscribe_request3), oauth2Header(test_user), status=200)

        # Index by username to be able to make asserts
        # This is mandatory, as we cannot assume the order of the queue
        messages = self.rabbit.get_all('syncacl')
        messages = {item[0]['u']['u']: item[0] for item in messages}

        self.assertEqual(len(messages), 2)

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
        from .mockers import batch_subscribe_request4
        from .mockers import context as context
        from .mockers import initial_subscriptions as subscriptions

        http_mock_info()
        http_mock_get_context(context)
        http_mock_get_context_subscriptions(subscriptions)

        self.testapp.post('/api/domains/test/services/syncacl'.format(), json.dumps(batch_subscribe_request4), oauth2Header(test_user), status=200)

        # Index by username to be able to make asserts
        # This is mandatory, as we cannot assume the order of the queue
        messages = self.rabbit.get_all('syncacl')
        messages = {item[0]['u']['u']: item[0] for item in messages}

        self.assertEqual(len(messages), 1)

        # Test subscribed user revoke permission, preserves most important role
        self.assertItemsEqual(messages['testuser.creator']['d']['tasks'], ['grant'])
        self.assertItemsEqual(messages['testuser.creator']['d']['tasks']['grant'], ['flag'])
        self.assertIn('context', messages['testuser.creator']['d'])


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
