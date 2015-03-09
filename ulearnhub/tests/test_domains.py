# -*- coding: utf-8 -*-
from paste.deploy import loadapp
from ulearnhub.tests import test_user
from ulearnhub.tests.utils import oauth2Header
from ulearnhub.tests.utils import UlearnhubTestApp

from ulearnhub.tests.mock_http import http_mock_checktoken

import httpretty
import json
import os
import unittest
from pyramid.request import Request


class FakeRequest(Request):
    def __init__(self, registry):
        self.registry = registry


class DomainTests(unittest.TestCase):

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

    def initialize_zodb(self):
        self.testapp.get('/initialize')

    def create_domain(self, **kwargs):
        """
            Create a domain
        """
        result = self.testapp.post('/api/domains', json.dumps(kwargs), oauth2Header(test_user), status=201)
        return result.json

    def test_initialize(self):
        from ulearnhub import root_factory
        from ulearnhub.models.deployments import Deployments, Deployment
        from ulearnhub.models.domains import Domains, Domain

        request = FakeRequest(self.testapp.testapp.app.registry)
        root = root_factory(request)

        self.assertEqual(root['domains'].__class__, Domains)
        self.assertEqual(root['deployments'].__class__, Deployments)

        self.assertEqual(root['domains']['test'].__class__, Domain)
        self.assertEqual(root['deployments']['test'].__class__, Deployment)

        self.assertEqual(root['deployments']['test'].__class__, Deployment)

    def test_register_domain(self):
        from .mockers import test_domain

        result = self.testapp.post('/api/domains', json.dumps(test_domain), oauth2Header(test_user), status=201)
        self.assertEqual(result.json['name'], test_domain['name'])
        self.assertEqual(result.json['server'], test_domain['server'])

    def test_get_domain(self):
        from .mockers import test_domain

        self.create_domain(**test_domain)
        result = self.testapp.get('/api/domains/{}'.format(test_domain['name']), {}, oauth2Header(test_user), status=200)

        self.assertEqual(result.json['name'], test_domain['name'])
        self.assertEqual(result.json['server'], test_domain['server'])

