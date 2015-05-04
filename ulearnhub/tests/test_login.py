# -*- coding: utf-8 -*-
from paste.deploy import loadapp
from ulearnhub.resources import create_defaults
from ulearnhub.tests import test_user
from ulearnhub.tests import UlearnHUBBaseTestCase
from ulearnhub.tests import oauth2Header
from ulearnhub.tests import BASE_DOMAIN
from ulearnhub.tests.utils import UlearnhubTestApp

from ulearnhub.tests.mockers.http import http_mock_checktoken
from ulearnhub.tests.mockers.http import http_mock_gettoken
from ulearnhub.tests.mockers.http import http_mock_user_info
from ulearnhub.tests.mockers.http import http_mock_info

import httpretty
import json
import os


class LoginTests(UlearnHUBBaseTestCase):

    def setUp(self):
        conf_dir = os.path.dirname(__file__)
        self.app = loadapp('config:tests.ini', relative_to=conf_dir)

        httpretty.enable()
        http_mock_info()
        http_mock_user_info()
        http_mock_checktoken()
        http_mock_gettoken()

        self.testapp = UlearnhubTestApp(self)
        create_defaults(self.testapp.testapp.app.registry, BASE_DOMAIN, quiet=True)
        self.initialize_test_deployment()
        self.patches = []

    def tearDown(self):
        httpretty.disable()

        for testpatch in self.patches:
            testpatch.stop()

    def test_get_domain_unauthenticated(self):
        res = self.testapp.get('/base', status=200)
        self.assertIn('form-signin', res.body)

    def test_get_root_login(self):
        res = self.testapp.get('/login', status=200)
        self.assertIn('form-signin', res.body)
        self.assertIn('id="inputDomain"', res.body)

    def test_get_domain_login(self):
        res = self.testapp.get('/base/login', status=200)
        self.assertIn('form-signin', res.body)
        self.assertNotIn('name="domain"', res.body)

    def test_root_login(self):
        params = {
            "username": "testuser",
            "password": "testpassword",
            "domain": "base",
            "form.submitted": 1
        }
        res = self.testapp.post('/login', params, status=302)
        self.assertEqual(res.headers['location'], 'http://localhost/base')

        self.assertIn('base_auth_tkt', self.testapp.testapp.cookies)
        logged = res.follow()
        self.assertIn('ng-app="uLearnHUB"', logged.body)

    def test_domain_login(self):
        params = {
            "username": "testuser",
            "password": "testpassword",
            "form.submitted": 1
        }
        res = self.testapp.post('/base/login', params, status=302)
        self.assertEqual(res.headers['location'], 'http://localhost/base')

        self.assertIn('base_auth_tkt', self.testapp.testapp.cookies)
        logged = res.follow()
        self.assertIn('ng-app="uLearnHUB"', logged.body)
