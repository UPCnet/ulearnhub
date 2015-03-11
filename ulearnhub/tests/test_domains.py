# -*- coding: utf-8 -*-
from paste.deploy import loadapp
from ulearnhub.tests import test_user
from ulearnhub.tests import UlearnHUBBaseTestCase
from ulearnhub.tests.utils import oauth2Header
from ulearnhub.tests.utils import UlearnhubTestApp

from ulearnhub.tests.mockers.http import http_mock_checktoken

import httpretty
import json
import os
from pyramid.request import Request


class FakeRequest(Request):
    def __init__(self, registry):
        self.registry = registry


class DomainTests(UlearnHUBBaseTestCase):

    def setUp(self):
        conf_dir = os.path.dirname(__file__)
        self.app = loadapp('config:tests.ini', relative_to=conf_dir)

        self.testapp = UlearnhubTestApp(self)
        self.initialize_zodb()
        self.patches = []

        httpretty.enable()
        http_mock_checktoken()

    def tearDown(self):
        httpretty.disable()

        for testpatch in self.patches:
            testpatch.stop()

    def create_domain(self, **kwargs):
        """
            Create a domain
        """
        result = self.testapp.post('/api/domains', json.dumps(kwargs), oauth2Header(test_user), status=201)
        return result.json

    def test_register_domain(self):
        from .mockers.domains import test_domain

        result = self.testapp.post('/api/domains', json.dumps(test_domain), oauth2Header(test_user), status=201)
        self.assertEqual(result.json['name'], test_domain['name'])
        self.assertEqual(result.json['server'], test_domain['server'])

    def test_get_domain(self):
        from .mockers.domains import test_domain

        self.create_domain(**test_domain)
        result = self.testapp.get('/api/domains/{}'.format(test_domain['name']), {}, oauth2Header(test_user), status=200)

        self.assertEqual(result.json['name'], test_domain['name'])
        self.assertEqual(result.json['server'], test_domain['server'])

