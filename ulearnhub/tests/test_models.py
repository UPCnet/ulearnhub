# -*- coding: utf-8 -*-
from paste.deploy import loadapp
from ulearnhub.models.domains import Domain
from ulearnhub.tests import test_user
from ulearnhub.tests.utils import oauth2Header
from ulearnhub.tests.utils import UlearnhubTestApp
from ulearnhub.tests.utils import mock_post

import json
import os
import unittest
from mock import patch
from functools import partial


class UlearnhubTests(unittest.TestCase):

    def setUp(self):
        conf_dir = os.path.dirname(__file__)
        self.app = loadapp('config:tests.ini', relative_to=conf_dir)
        self.patched_post = patch('requests.post', new=partial(mock_post, self))
        self.patched_post.start()
        self.testapp = UlearnhubTestApp(self)
        self.initialize_zodb()

    def initialize_zodb(self):
        self.testapp.get('/initialize')

    def tearDown(self):
        pass

    def create_domain(self, **kwargs):
        result = self.testapp.post('/api/domains', json.dumps(kwargs), oauth2Header(test_user), status=201)
        return result.json

    def get_last(self, klass, pos=-1):
        results = self.session.query(klass).all()
        if results:
            return results[pos]
        else:
            return None

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
