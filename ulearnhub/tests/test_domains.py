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


class DomainTests(UlearnHUBBaseTestCase):

    def setUp(self):
        conf_dir = os.path.dirname(__file__)
        self.app = loadapp('config:tests.ini', relative_to=conf_dir)

        httpretty.enable()
        http_mock_info()
        http_mock_checktoken()

        self.testapp = UlearnhubTestApp(self)
        self.initialize_empty_zodb(self.testapp.testapp.app.registry)
        self.initialize_test_deployment()
        self.patches = []

    def tearDown(self):
        httpretty.disable()

        for testpatch in self.patches:
            testpatch.stop()

    def test_register_domain(self):
        from .mockers.domains import test_domain

        res = self.testapp.post('/api/domains', json.dumps(test_domain), oauth2Header(test_user), status=201)
        self.assertEqual(res.json['name'], test_domain['name'])
        self.assertEqual(res.json['title'], test_domain['title'])
        self.assertEqual(res.json['max'], None)
        self.assertEqual(res.json['oauth'], None)

    def test_get_domain(self):
        from .mockers.domains import test_domain
        res = self.create_domain(test_domain)

        self.assertEqual(res.json['name'], test_domain['name'])
        self.assertEqual(res.json['title'], test_domain['title'])
        self.assertEqual(res.json['max'], None)
        self.assertEqual(res.json['oauth'], None)

    def test_assign_component(self):
        from .mockers.domains import test_domain
        self.create_domain(test_domain)
        res = self.testapp.post('/api/domains/{}/components'.format(test_domain['name']), json.dumps({'component_id': 'test/maxserver:testmaxserver1'}), oauth2Header(test_user), status=201)

        self.assertEqual(res.json['name'], test_domain['name'])
        self.assertEqual(res.json['title'], test_domain['title'])
        self.assertEqual(res.json['max'], 'http://localhost:8081')
        self.assertEqual(res.json['oauth'], 'https://oauth.upcnet.es')
