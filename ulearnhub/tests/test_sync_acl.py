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
    def patched(*args, **kwargs):
        return response
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


class UlearnhubTests(unittest.TestCase):

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

        ldap_config = {
            "server": "ldap-pre.upc.edu",
            "name": "ldapUPC",
            "port": 636,
            "base_dn": "dc=upc,dc=edu",
            "admin_cn": "ulearn.consulta",
            "admin_password": "",
            "branch_admin_cn": "ulearn.consulta",
            "branch_admin_password": "",
            "branch_users_dn": "ou=Users",
            "branch_groups_dn": "ou=Groups",
            "base_users": [
                {"username": "upcnet.manteniment", "password": ""},
                {"username": "ulearn.user1", "password": ""},
                {"username": "ulearn.user2", "password": ""},
                {"username": "ulearn.user3", "password": ""}
            ]
        }

        maxcluster = MaxCluster('Test Max Cluster')
        maxserver = MaxServer('Test Max Server', url='http://localhost:8081')
        ldapserver = LdapServer('LDAP UPC', readonly=True, config=ldap_config)
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

    def test_domain_syncacl(self):
        from .mockers import batch_subscribe_request
        from .mockers import context as context
        from .mockers import initial_subscriptions as subscriptions
        from .mockers import ldap_test_group

        http_mock_info()
        http_mock_get_context(context)
        http_mock_get_context_subscriptions(subscriptions)

        self.add_patch(ldap_patch_connect())
        self.add_patch(ldap_patch_disconnect())
        self.add_patch(ldap_patch_group_search(ldap_test_group))
        result = self.testapp.post('/api/domains/test/services/syncacl'.format(), json.dumps(batch_subscribe_request), oauth2Header(test_user), status=200)

        messages = self.rabbit.get_all('syncacl')
        import ipdb;ipdb.set_trace()

