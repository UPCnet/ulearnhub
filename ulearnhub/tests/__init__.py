# -*- coding: utf-8 -*-
import unittest
from pyramid.request import Request
import transaction


test_user = 'carles.bruguera'
MOCK_TOKEN = "jfa1sDF2SDF234"
RABBIT_URL = "amqp://guest:guest@localhost:5672"
TEST_VHOST_URL = '{}/tests'.format(RABBIT_URL)
RABBIT_MANAGEMENT_URL = "http://localhost:15672/api".format(RABBIT_URL)


class FakeRequest(Request):
    def __init__(self, registry):
        self.registry = registry


class UlearnHUBBaseTestCase(unittest.TestCase):

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
