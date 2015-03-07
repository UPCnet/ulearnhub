# -*- coding: utf-8 -*-
from paste.deploy import loadapp
from ulearnhub.tests import test_user
from ulearnhub.tests.utils import oauth2Header
from ulearnhub.tests.utils import UlearnhubTestApp
from ulearnhub.tests.utils import mock_get, mock_post

import json
import os
import unittest
from mock import patch
from functools import partial

from pyramid.request import Request


class FakeRequest(Request):
    def __init__(self, registry):
        self.registry = registry


class UlearnhubTests(unittest.TestCase):

    def setUp(self):
        conf_dir = os.path.dirname(__file__)
        self.app = loadapp('config:tests.ini', relative_to=conf_dir)
        self.patched_post = patch('requests.post', new=partial(mock_post, self))
        self.patched_post.start()

        self.patched_get = patch('requests.get', new=partial(mock_get, self))
        self.patched_get.start()

        self.testapp = UlearnhubTestApp(self)
        self.initialize_zodb()

    def initialize_zodb(self):
        self.testapp.get('/initialize')

    def tearDown(self):
        self.patched_post.stop()
        self.patched_get.stop()

    def create_domain(self, **kwargs):
        result = self.testapp.post('/api/domains', json.dumps(kwargs), oauth2Header(test_user), status=201)
        return result.json

    def get_last(self, klass, pos=-1):
        results = self.session.query(klass).all()
        if results:
            return results[pos]
        else:
            return None

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

    def test_domain_batchsubscriber(self):
        from .mockers import batch_subscribe_request
        result = self.testapp.post('/api/domains/test/services/batchsubscriber'.format(), json.dumps(batch_subscribe_request), oauth2Header(test_user), status=200)

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

