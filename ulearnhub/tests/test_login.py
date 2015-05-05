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
        self.initialize_test_domain()

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
        """
            Given a user logging onto root
            When the login has been validated
            Then i'm redirected to the root page
            And i have both root and domain cookies set
        """
        params = {
            "username": "testuser",
            "password": "testpassword",
            "domain": "base",
            "form.submitted": 1
        }
        res = self.testapp.post('/login', params, status=302)
        self.assertEqual(res.headers['location'], 'http://localhost')

        self.assertIn('auth_tkt', self.testapp.testapp.cookies)
        self.assertIn('base_auth_tkt', self.testapp.testapp.cookies)
        logged = res.follow()
        self.assertIn('ng-app="uLearnHUB"', logged.body)

    def test_domain_login(self):
        """
            Given a user logging onto domain
            When the login has been validated
            Then i'm redirected to the domain page
            And i have domain cookies set
            And i don't have root cookies set
        """
        params = {
            "username": "testuser",
            "password": "testpassword",
            "form.submitted": 1
        }
        res = self.testapp.post('/base/login', params, status=302)
        self.assertEqual(res.headers['location'], 'http://localhost/base')

        self.assertIn('base_auth_tkt', self.testapp.testapp.cookies)
        self.assertNotIn('auth_tkt', self.testapp.testapp.cookies)
        logged = res.follow()
        self.assertIn('ng-app="uLearnHUB"', logged.body)

    def test_domain_login_check_other(self):
        """
            Given a user logging onto domain
            When the login has been validated
            Then i'm redirected to the domain page
            And i have domain cookies set
            And i'm not logged on other domains
        """
        params = {
            "username": "testuser",
            "password": "testpassword",
            "form.submitted": 1
        }
        res = self.testapp.post('/base/login', params, status=302)
        self.assertEqual(res.headers['location'], 'http://localhost/base')

        res = self.testapp.get('/test', status=200)
        self.assertNotIn('ng-app="uLearnHUB"', res.body)
        self.assertIn('form-signin', res.body)

    def test_double_domain_login(self):
        """
            Given a user logging onto two domains
            When the logins has been validated
            And i have domain cookies set from both domains
        """
        params = {
            "username": "testuser",
            "password": "testpassword",
            "form.submitted": 1
        }
        res = self.testapp.post('/base/login', params, status=302)
        self.assertEqual(res.headers['location'], 'http://localhost/base')

        res = self.testapp.post('/test/login', params, status=302)
        self.assertEqual(res.headers['location'], 'http://localhost/test')

        self.assertIn('base_auth_tkt', self.testapp.testapp.cookies)
        self.assertIn('test_auth_tkt', self.testapp.testapp.cookies)

        res = self.testapp.get('/base', status=200)
        self.assertIn('ng-app="uLearnHUB"', res.body)

        res = self.testapp.get('/test', status=200)
        self.assertIn('ng-app="uLearnHUB"', res.body)

    def test_double_domain_login_one_logout(self):
        """
            Given a user logging onto two domains
            When the logins has been validated
            And i log out of one of the domains
            Then i can access one domain
            And i cannot access the logged out one
        """
        params = {
            "username": "testuser",
            "password": "testpassword",
            "form.submitted": 1
        }
        res = self.testapp.post('/base/login', params, status=302)
        self.assertEqual(res.headers['location'], 'http://localhost/base')

        res = self.testapp.post('/test/login', params, status=302)
        self.assertEqual(res.headers['location'], 'http://localhost/test')

        self.assertIn('base_auth_tkt', self.testapp.testapp.cookies)
        self.assertIn('test_auth_tkt', self.testapp.testapp.cookies)

        self.testapp.get('/base/logout', status=302)

        res = self.testapp.get('/base', status=200)
        self.assertNotIn('ng-app="uLearnHUB"', res.body)

        res = self.testapp.get('/test', status=200)
        self.assertIn('ng-app="uLearnHUB"', res.body)

    def test_domain_logout(self):
        """
            Given a user logged un a domain
            When the user logs out
            Then i cannot access the domain page
        """
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
        self.testapp.get('/base/logout', status=302)
        res = self.testapp.get('/base', status=200)
        self.assertNotIn('ng-app="uLearnHUB"', res.body)
        self.assertIn('form-signin', res.body)

    def test_root_logout(self):
        """
            Given a user logged on two domains
            When the user logs out on root
            Then i get logged out from root
            And i get logged out from both domains
        """
        params = {
            "username": "testuser",
            "password": "testpassword",
            "form.submitted": 1
        }
        res = self.testapp.post('/base/login', params, status=302)
        self.assertEqual(res.headers['location'], 'http://localhost/base')

        res = self.testapp.post('/test/login', params, status=302)
        self.assertEqual(res.headers['location'], 'http://localhost/test')

        self.assertIn('auth_tkt', self.testapp.testapp.cookies)
        self.assertIn('base_auth_tkt', self.testapp.testapp.cookies)
        self.assertIn('test_auth_tkt', self.testapp.testapp.cookies)

        self.testapp.get('/logout', status=302)

        res = self.testapp.get('/', status=200)
        self.assertIn('form-signin', res.body)

        res = self.testapp.get('/base', status=200)
        self.assertIn('form-signin', res.body)

        res = self.testapp.get('/test', status=200)
        self.assertIn('form-signin', res.body)
