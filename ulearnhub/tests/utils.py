# -*- coding: utf-8 -*-
import cookielib


class UlearnhubTestApp(object):

    def __init__(self, testcase, keep_cookies=False):
        from webtest import TestApp
        self.testcase = testcase
        cookiejar = cookielib.CookieJar()
        self.testapp = TestApp(testcase.app, cookiejar=cookiejar)

    def get(self, *args, **kwargs):
        return self.call_testapp('get', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.call_testapp('post', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.call_testapp('put', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.call_testapp('delete', *args, **kwargs)

    def head(self, *args, **kwargs):
        return self.call_testapp('head', *args, **kwargs)

    def call_testapp(self, method, *args, **kwargs):

        status = kwargs.get('status', None)
        headers = kwargs.setdefault('headers', {})
        testapp_method = getattr(self.testapp, method)
        kwargs['expect_errors'] = True
        res = testapp_method(*args, **kwargs)
        if status is not None:
            message = "Response status is {},  we're expecting {}. ".format(res.status_int, status)
            if hasattr(res, 'json'):
                if 'error' in getattr(res, 'json', []):
                    message += '\nRaised {error}: "{error_description}"'.format(**res.json)
            self.testcase.assertEqual(status, res.status_int, message)
        return res
