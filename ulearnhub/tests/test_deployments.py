# -*- coding: utf-8 -*-
from paste.deploy import loadapp
from ulearnhub.tests import test_user
from ulearnhub.tests import UlearnHUBBaseTestCase
from ulearnhub.tests import oauth2Header
from ulearnhub.tests.utils import UlearnhubTestApp

from ulearnhub.tests.mockers.http import http_mock_checktoken
from ulearnhub.tests.mockers.http import http_mock_info

import httpretty
import json
import os


class DeploymentsTests(UlearnHUBBaseTestCase):

    def setUp(self):
        conf_dir = os.path.dirname(__file__)
        self.app = loadapp('config:tests.ini', relative_to=conf_dir)

        self.testapp = UlearnhubTestApp(self)
        self.initialize_empty_zodb(self.testapp.testapp.app.registry)
        self.patches = []

        httpretty.enable()
        http_mock_checktoken()

    def tearDown(self):
        httpretty.disable()

        for testpatch in self.patches:
            testpatch.stop()

    # BEGIN TESTS

    def test_create_deployment(self):
        from .mockers.deployments import test_deployment

        res = self.testapp.post('/api/deployments', json.dumps(test_deployment), headers=oauth2Header(test_user), status=201)
        self.assertEqual(res.json['name'], test_deployment['name'])
        self.assertEqual(res.json['title'], test_deployment['title'])

    def test_get_deployment(self):
        from .mockers.deployments import test_deployment

        self.create_deployment(test_deployment)
        res = self.testapp.get('/api/deployments/{}'.format(test_deployment['name']), '', headers=oauth2Header(test_user), status=200)
        self.assertEqual(res.json['name'], test_deployment['name'])
        self.assertEqual(res.json['title'], test_deployment['title'])

    def test_add_component_ldap(self):
        from .mockers.deployments import test_deployment
        from .mockers.deployments import test_ldap_component as component

        self.create_deployment(test_deployment)
        res = self.testapp.post('/api/deployments/{}/components'.format(test_deployment['name']), json.dumps(component), headers=oauth2Header(test_user), status=201)
        self.assertEqual(res.json['server'], component['params']['server'])

    def test_add_component_maxcluster(self):
        from .mockers.deployments import test_deployment
        from .mockers.deployments import test_maxcluster_component as component

        self.create_deployment(test_deployment)
        res = self.testapp.post('/api/deployments/{}/components'.format(test_deployment['name']), json.dumps(component), headers=oauth2Header(test_user), status=201)
        self.assertEqual(res.json['server'], component['params']['server'])

    def test_add_component_maxserver(self):
        from .mockers.deployments import test_deployment
        from .mockers.deployments import test_maxcluster_component as max_cluster
        from .mockers.deployments import test_maxserver_component as component

        http_mock_info()
        self.create_deployment(test_deployment)
        self.add_component(test_deployment, max_cluster)
        res = self.testapp.post('/api/deployments/{}/components'.format(test_deployment['name']), json.dumps(component), headers=oauth2Header(test_user), status=201)
        self.assertEqual(res.json['url'], component['params']['url'])

        res = self.testapp.get('/api/deployments/{}'.format(test_deployment['name']), '', headers=oauth2Header(test_user), status=200)
        self.assertEqual(res.json['components']['testmaxcluster']['components']['testmaxserver1']['url'], component['params']['url'])
