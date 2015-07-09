# -*- coding: utf-8 -*-
from maxcarrot import RabbitClient

from ulearnhub.resources import create_defaults
from ulearnhub.tests.mockers.deployments import TEST_VHOST_URL
from ulearnhub.tests import UlearnHUBBaseTestCase
from ulearnhub.tests import test_user
from ulearnhub.tests.mockers.http import http_mock_checktoken
from ulearnhub.tests.mockers.http import http_mock_get_context
from ulearnhub.tests.mockers.http import http_mock_get_context_subscriptions
from ulearnhub.tests.mockers.http import http_mock_group_communities
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


class UlearnhubSyncLDAPGroupFunctionalTests(UlearnHUBBaseTestCase):

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

    def test_syncldapgroup(self):
        """
        """
        from .mockers.syncgroup import update_group_request
        from .mockers.syncacl import context
        from .mockers.syncacl import initial_subscriptions as subscriptions
        from .mockers.syncacl import ldap_test_group4

        http_mock_group_communities([
            {
                'url': context['url'],
                'groups': [],
                'users': ['testuser1.creator']
            }
        ])
        http_mock_get_context(context)
        http_mock_get_context_subscriptions(subscriptions)

        self.add_patch(ldap_patch_connect())
        self.add_patch(ldap_patch_disconnect())
        self.add_patch(ldap_patch_group_search({
            'group4': ldap_test_group4,

        }))

        self.testapp.post(
            '/api/deployments/{deployment}/components/{component}/services/{service}'.format(
                deployment='test',
                component='testldap',
                service='syncldapgroup'
            ),
            json.dumps(update_group_request), headers=oauth2Header(test_user), status=200)

        # Index by username to be able to make asserts
        # This is mandatory, as we cannot assume the order of the queue
        messages = self.assertMessagesInQueue('syncacl', retries=3, expected=1)

        # Test subscribed user revoke permission, preserves most important role
        self.assertItemsEqual(messages['groupuser1']['d']['tasks'], ['subscribe'])
        self.assertIn('context', messages['groupuser1']['d'])


class UlearnhubSyncLDAPGroupIntersectingUnitTests(unittest.TestCase):

    def test_intersect_new_user(self):
        """
            Given a new user in ldap
            And there are no individually assigned users
            And there are no grup assigned users
            When i calculate the subscriptions/unsubscriptions to perform
            Then the new user is in the subscriptions list
            And no one in in the unsubscriptions list
        """
        from ulearnhub.models.utils import intersect_users

        new_users = [3]
        ldap_users = [1, 2] + new_users
        community_group_users = []
        community_users = []
        context_users = [1, 2]

        subscriptions, unsubscriptions = intersect_users(
            ldap_users,
            community_group_users,
            community_users,
            context_users
        )

        self.assertItemsEqual(subscriptions, [3])
        self.assertItemsEqual(unsubscriptions, [])

    def test_intersect_new_users(self):
        """
            Given new users in ldap
            And there are no individually assigned users
            And there are no grup assigned users
            When i calculate the subscriptions/unsubscriptions to perform
            Then the new users are in the subscriptions list
            And no one in in the unsubscriptions list
        """
        from ulearnhub.models.utils import intersect_users

        new_users = [3, 4]
        ldap_users = [1, 2] + new_users
        community_group_users = []
        community_users = []
        context_users = [1, 2]

        subscriptions, unsubscriptions = intersect_users(
            ldap_users,
            community_group_users,
            community_users,
            context_users
        )

        self.assertItemsEqual(subscriptions, [3, 4])
        self.assertItemsEqual(unsubscriptions, [])

    def test_intersect_new_user_individually_subscribed(self):
        """
            Given a new user in ldap
            And the user is individually subscribed
            And there are no grup assigned users
            When i calculate the subscriptions/unsubscriptions to perform
            Then no one is in the subscriptions list
            And no one is in the unsubscriptions list
        """
        from ulearnhub.models.utils import intersect_users

        new_users = [3]
        ldap_users = [1, 2] + new_users
        community_group_users = []
        community_users = [3]
        context_users = [1, 2, 3]

        subscriptions, unsubscriptions = intersect_users(
            ldap_users,
            community_group_users,
            community_users,
            context_users
        )

        self.assertItemsEqual(subscriptions, [])
        self.assertItemsEqual(unsubscriptions, [])

    def test_intersect_new_user_other_group_subscribed(self):
        """
            Given new users in ldap
            And there are no individually assigned users
            And the new user is subscribed via another group
            When i calculate the subscriptions/unsubscriptions to perform
            Then no one is in the subscriptions list
            And no one is in the unsubscriptions list
        """
        from ulearnhub.models.utils import intersect_users

        new_users = [3]
        ldap_users = [1, 2] + new_users
        community_group_users = [3, 2]
        community_users = []
        context_users = [1, 2, 3]

        subscriptions, unsubscriptions = intersect_users(
            ldap_users,
            community_group_users,
            community_users,
            context_users
        )

        self.assertItemsEqual(subscriptions, [])
        self.assertItemsEqual(unsubscriptions, [])

    def test_intersect_new_user_individually_and_other_group_subscribed(self):
        """
            Given new users in ldap
            And the new user is individually assigned
            And the new user is also subscribed via another group
            When i calculate the subscriptions/unsubscriptions to perform
            Then no one is in the subscriptions list
            And no one is in the unsubscriptions list
        """
        from ulearnhub.models.utils import intersect_users

        new_users = [3]
        ldap_users = [1, 2] + new_users
        community_group_users = [3, 2]
        community_users = [3]
        context_users = [1, 2, 3]

        subscriptions, unsubscriptions = intersect_users(
            ldap_users,
            community_group_users,
            community_users,
            context_users
        )

        self.assertItemsEqual(subscriptions, [])
        self.assertItemsEqual(unsubscriptions, [])

    def test_intersect_drop_user(self):
        """
            Given a user is dropped on ldap
            And there are no individually assigned users
            And there are no grup assigned users
            When i calculate the subscriptions/unsubscriptions to perform
            Then no one is in the subscriptions list
            And the dropped user is in the unsubscriptions list
        """
        from ulearnhub.models.utils import intersect_users

        ldap_users = [1, 2, 3]
        ldap_users.remove(3)
        community_group_users = []
        community_users = []
        context_users = [1, 2, 3]

        subscriptions, unsubscriptions = intersect_users(
            ldap_users,
            community_group_users,
            community_users,
            context_users
        )

        self.assertItemsEqual(subscriptions, [])
        self.assertItemsEqual(unsubscriptions, [3])

    def test_intersect_drop_users(self):
        """
            Given a user is dropped on ldap
            And there are no individually assigned users
            And there are no grup assigned users
            When i calculate the subscriptions/unsubscriptions to perform
            Then no one is in the subscriptions list
            And the dropped user is in the unsubscriptions list
        """
        from ulearnhub.models.utils import intersect_users

        ldap_users = [1, 2, 3, 4]
        ldap_users.remove(3)
        ldap_users.remove(4)
        community_group_users = []
        community_users = []
        context_users = [1, 2, 3, 4]

        subscriptions, unsubscriptions = intersect_users(
            ldap_users,
            community_group_users,
            community_users,
            context_users
        )

        self.assertItemsEqual(subscriptions, [])
        self.assertItemsEqual(unsubscriptions, [3, 4])

    def test_intersect_drop_users_individually_assigned(self):
        """
            Given a user is dropped on ldap
            And the user is individually assigned
            And there are no grup assigned users
            When i calculate the subscriptions/unsubscriptions to perform
            Then no one is in the subscriptions list
            And no one is in the unsubscriptions list
        """
        from ulearnhub.models.utils import intersect_users

        ldap_users = [1, 2, 3, 4]
        ldap_users.remove(4)
        community_group_users = []
        community_users = [4]
        context_users = [1, 2, 3, 4]

        subscriptions, unsubscriptions = intersect_users(
            ldap_users,
            community_group_users,
            community_users,
            context_users
        )

        self.assertItemsEqual(subscriptions, [])
        self.assertItemsEqual(unsubscriptions, [])

    def test_intersect_drop_users_group_assigned(self):
        """
            Given a user is dropped on ldap
            And there are no individually assigned users
            And the user is group assigned
            When i calculate the subscriptions/unsubscriptions to perform
            Then no one is in the subscriptions list
            And no one is in the unsubscriptions list
        """
        from ulearnhub.models.utils import intersect_users

        ldap_users = [1, 2, 3, 4]
        ldap_users.remove(4)
        community_group_users = [4, 3]
        community_users = []
        context_users = [1, 2, 3, 4]

        subscriptions, unsubscriptions = intersect_users(
            ldap_users,
            community_group_users,
            community_users,
            context_users
        )

        self.assertItemsEqual(subscriptions, [])
        self.assertItemsEqual(unsubscriptions, [])

    def test_intersect_drop_users_individually_and_group_assigned(self):
        """
            Given a user is dropped on ldap
            And the user is individually assigned
            And the user is group assigned
            When i calculate the subscriptions/unsubscriptions to perform
            Then no one is in the subscriptions list
            And no one is in the unsubscriptions list
        """
        from ulearnhub.models.utils import intersect_users

        ldap_users = [1, 2, 3, 4]
        ldap_users.remove(4)
        community_group_users = [4, 3]
        community_users = [4]
        context_users = [1, 2, 3, 4]

        subscriptions, unsubscriptions = intersect_users(
            ldap_users,
            community_group_users,
            community_users,
            context_users
        )

        self.assertItemsEqual(subscriptions, [])
        self.assertItemsEqual(unsubscriptions, [])

    def test_intersect_mixed_usecase_1(self):
        """
            Given some users are dropped on ldap
            And some users are added on ldap
            And no one is individually assigned
            And no one is group assigned
            When i calculate the subscriptions/unsubscriptions to perform
            Then new users are in the subscriptions list
            And dropped users are in the unsubscriptions list
        """
        from ulearnhub.models.utils import intersect_users

        ldap_users = [1, 2, 3, 4]
        ldap_users.remove(3)
        ldap_users.remove(4)
        ldap_users = ldap_users + [5, 6]
        community_group_users = []
        community_users = []
        context_users = [1, 2, 3, 4]

        subscriptions, unsubscriptions = intersect_users(
            ldap_users,
            community_group_users,
            community_users,
            context_users
        )

        self.assertItemsEqual(subscriptions, [5, 6])
        self.assertItemsEqual(unsubscriptions, [3, 4])

    def test_intersect_mixed_usecase_2(self):
        """
            Given some users are dropped on ldap
            And some users are added on ldap
            And some users are individually assigned
            And no one is group assigned
            When i calculate the subscriptions/unsubscriptions to perform
            Then new users are in the subscriptions list, except for the individually assigned (already subscribed)
            And dropped users are in the unsubscriptions list except for the individually assigned
        """
        from ulearnhub.models.utils import intersect_users

        ldap_users = [1, 2, 3, 4]
        ldap_users.remove(3)
        ldap_users.remove(4)
        ldap_users = ldap_users + [5, 6]
        community_group_users = []
        community_users = [3, 5]
        context_users = [1, 2, 3, 4, 5]

        subscriptions, unsubscriptions = intersect_users(
            ldap_users,
            community_group_users,
            community_users,
            context_users
        )

        self.assertItemsEqual(subscriptions, [6])
        self.assertItemsEqual(unsubscriptions, [4])

    def test_intersect_mixed_usecase_3(self):
        """
            Given some users are dropped on ldap
            And some users are added on ldap
            And no one is individually assigned
            And some users are group assigned
            When i calculate the subscriptions/unsubscriptions to perform
            Then new users are in the subscriptions list, except for the group assigned (already subscribed)
            And dropped users are in the unsubscriptions list except for the group assigned
        """
        from ulearnhub.models.utils import intersect_users

        ldap_users = [1, 2, 3, 4]
        ldap_users.remove(3)
        ldap_users.remove(4)
        ldap_users = ldap_users + [5, 6]
        community_group_users = [3, 5]
        community_users = []
        context_users = [1, 2, 3, 4, 5]

        subscriptions, unsubscriptions = intersect_users(
            ldap_users,
            community_group_users,
            community_users,
            context_users
        )

        self.assertItemsEqual(subscriptions, [6])
        self.assertItemsEqual(unsubscriptions, [4])

    def test_intersect_mixed_usecase_4(self):
        """
            Given some users are dropped on ldap
            And some users are added on ldap
            And some users are individually assigned
            And some users are group assigned
            When i calculate the subscriptions/unsubscriptions to perform
            Then new users are in the subscriptions list, except for the group assigned (already subscribed)
            And dropped users are in the unsubscriptions list except for the group assigned
        """
        from ulearnhub.models.utils import intersect_users

        other_group_1 = [1, 4, 8]
        other_group_2 = [2, 6, 9]

        previous_ldap_users = [0, 1, 2, 3, 4, 5, 6]
        ldap_users = previous_ldap_users + [
            7,   # 7 is not on other groups nor individually assigned --> added
            8,   # 8 is on group 1 and already subscribed --> pass
            9,   # 9 is on group 2 and individually assigned, and already subscribed --> pass
            10,  # 10 is individually assigned and already subscribed  --> pass
            11   # 11 is individually assigned but not subscribed (inconsistency) -- added>
        ]
        ldap_users.remove(3)  # 3 is not on other groups nor individually assigned --> removed
        ldap_users.remove(4)  # 4 is on group 1 --> preserved
        ldap_users.remove(5)  # 5 is individually assigned --> preserved
        ldap_users.remove(6)  # 6 is in group 2 and individually assigned --> preserved
        ldap_users.remove(0)  # 0 is individually assigned but not subscribed (inconsistency) --> pass

        community_group_users = other_group_1 + other_group_2
        community_users = [0, 5, 6, 9, 10, 11]
        context_users = [1, 2, 3, 4, 5, 6, 8, 9, 10]

        subscriptions, unsubscriptions = intersect_users(
            ldap_users,
            community_group_users,
            community_users,
            context_users
        )

        self.assertItemsEqual(subscriptions, [7, 11])
        self.assertItemsEqual(unsubscriptions, [3])
