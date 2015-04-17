# -*- coding: utf-8 -*-
from ulearnhub import root_factory
from ulearnhub.models.components import LdapServer
from ulearnhub.models.components import MaxCluster
from ulearnhub.models.components import MaxServer
from ulearnhub.models.components import RabbitServer
from ulearnhub.models.deployments import Deployment
from ulearnhub.models.deployments import Deployments
from ulearnhub.models.domains import Domain
from ulearnhub.models.domains import Domains

from pyramid.request import Request

import json
import transaction
import unittest


test_user = 'carles.bruguera'
MOCK_TOKEN = "jfa1sDF2SDF234"
RABBIT_URL = "amqp://guest:guest@localhost:5672"
TEST_VHOST_URL = '{}/tests'.format(RABBIT_URL)
RABBIT_MANAGEMENT_URL = "http://localhost:15672/api".format(RABBIT_URL)


def oauth2Header(username, token=MOCK_TOKEN, scope="widgetcli"):
    return {
        "X-Oauth-Token": token,
        "X-Oauth-Username": username,
        "X-Oauth-Scope": scope}


class FakeRequest(Request):
    def __init__(self, registry):
        self.registry = registry


class UlearnHUBBaseTestCase(unittest.TestCase):

    def add_patch(self, testpatch):
        self.patches.append(testpatch)
        testpatch.start()

    def create_deployment(self, deployment, status=201):
        return self.testapp.post('/api/deployments', json.dumps(deployment), headers=oauth2Header(test_user), status=status)

    def add_component(self, deployment, component, status=201):
        return self.testapp.post('/api/deployments/{}/components'.format(deployment['name']), json.dumps(component), headers=oauth2Header(test_user), status=status)

    def create_domain(self, domain, status=201):
        return self.testapp.post('/api/domains', json.dumps(domain), oauth2Header(test_user), status=status)

    def initialize_empty_zodb(self):
        request = FakeRequest(self.testapp.testapp.app.registry)
        root = root_factory(request)
        root['deployments'] = Deployments()
        root['domains'] = Domains()
        transaction.commit()
        return root

    def initialize_test_deployment(self):
        from ulearnhub.tests.mockers.deployments import test_deployment
        from ulearnhub.tests.mockers.deployments import test_ldap_component
        from ulearnhub.tests.mockers.deployments import test_maxcluster_component
        from ulearnhub.tests.mockers.deployments import test_maxserver_component
        self.create_deployment(test_deployment)
        self.add_component(test_deployment, test_ldap_component)
        self.add_component(test_deployment, test_maxcluster_component)
        self.add_component(test_deployment, test_maxserver_component)

    def initialize_test_domain(self):
        self.create_domain()

        # test_domain = domains['test'] = Domain(name='test', title='Test Domain')
        # test_domain.components.append(ldapserver)
        # test_domain.components.append(maxserver)
        # test_domain.components.append(rabbitserver)

