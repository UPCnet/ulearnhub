# -*- coding: utf-8 -*-
import json
import unittest


test_user = 'test.user'
MOCK_TOKEN = "jfa1sDF2SDF234"

BASE_DOMAIN = {
    "deployments": {
        "base": {
            "title": "Local deployment",
            "components": [
                {
                    "type": "maxcluster",
                    "name": "basecluster",
                    "title": "Base MAX Server Cluster",
                    "config": {}
                },
                {
                    "type": "maxserver",
                    "name": "base",
                    "title": "Base MAX Server",
                    "config": {
                        "url": "http://localhost:8081"
                    }
                }
            ]
        }
    },
    "domains": {
        "base": {
            "title": "Base domain",
            "components": [
                {
                    "deployment": "base",
                    "type": "maxserver",
                    "name": "base"
                }
            ]
        }
    },
    "users": [
        {"domain": "base", "username": "test.user", "roles": ["Manager"]}
    ]
}


def oauth2Header(username, token=MOCK_TOKEN, scope="widgetcli", domain='base'):
    return {
        "Content-Type": "application/json",
        "X-Oauth-Token": token,
        "X-Oauth-Username": username,
        "X-Oauth-Scope": scope,
        "X-Oauth-Domain": domain}


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

    def initialize_empty_zodb(self, registry, defaults={}):
        from ulearnhub.resources import create_defaults
        return create_defaults(registry, defaults)

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


import warnings
warnings.filterwarnings("ignore")
