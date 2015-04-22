# -*- coding: utf-8 -*-
from collections import namedtuple

import json
import unittest


test_user = 'carles.bruguera'
MOCK_TOKEN = "jfa1sDF2SDF234"


def oauth2Header(username, token=MOCK_TOKEN, scope="widgetcli"):
    return {
        "X-Oauth-Token": token,
        "X-Oauth-Username": username,
        "X-Oauth-Scope": scope}


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

    def assign_component(self, domain_name, component_id, status=201):
        return self.testapp.post('/api/domains/{}/components'.format(domain_name), json.dumps({'component_id': component_id}), oauth2Header(test_user), status=201)

    def initialize_empty_zodb(self, registry):
        from ulearnhub import get_static_connection, bootstrap

        connection = get_static_connection(registry)
        root = bootstrap(connection.root())
        return root

    def initialize_test_deployment(self):
        from ulearnhub.tests.mockers.deployments import test_deployment
        from ulearnhub.tests.mockers.deployments import test_ldap_component
        from ulearnhub.tests.mockers.deployments import test_maxcluster_component
        from ulearnhub.tests.mockers.deployments import test_maxserver_component
        from ulearnhub.tests.mockers.deployments import test_rabbitserver_component

        self.create_deployment(test_deployment)
        self.add_component(test_deployment, test_rabbitserver_component)
        self.add_component(test_deployment, test_ldap_component)
        self.add_component(test_deployment, test_maxcluster_component)
        self.add_component(test_deployment, test_maxserver_component)

    def initialize_test_domain(self):
        from ulearnhub.tests.mockers.domains import test_domain
        self.create_domain(test_domain)
        self.assign_component(test_domain['name'], 'test/maxserver:testmaxserver1')
        self.assign_component(test_domain['name'], 'test/ldapserver:testldap')
        self.assign_component(test_domain['name'], 'test/rabbitserver:testrabbit')
