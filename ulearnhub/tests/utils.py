from ulearnhub.tests import MOCK_TOKEN
from ulearnhub.tests import test_user

import json

def oauth2Header(username, token=MOCK_TOKEN, scope="widgetcli"):
    return {
        "X-Oauth-Token": token,
        "X-Oauth-Username": username,
        "X-Oauth-Scope": scope}


class UlearnhubTestApp(object):

    def __init__(self, testcase):
        from webtest import TestApp
        self.testcase = testcase
        self.testapp = TestApp(testcase.app)

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


class mock_requests_obj(object):

    def __init__(self, *args, **kwargs):
        if kwargs.get('text', None) is not None:
            self.content = self.text = kwargs['text']
        elif kwargs.get('content', None) is not None:
            self.content = self.text = kwargs['content']
        self.status_code = kwargs['status_code']

    def json(self):
        return json.loads(self.text)


def mock_get(self, url, *args, **kwargs):  # pragma: no cover
    #Return OK to any post request targeted to 'checktoken', with the mock token
    if url.endswith('/info'):
        info = {
            "max.oauth_server": "https://oauth.upcnet.es",
            "version": "4.0.26.dev0",
            "max.server_id": "test"
        }
        return mock_requests_obj(text=json.dumps(info), status_code=200)
    elif url.endswith('/contexts/ae74c10247cc37aed30b52391bb8d32d90c011d1'):
        context = {
            "displayName": "Test",
            "url": "http://localhost/communities/testcommunity",
            "permissions": {
                "write": "restricted",
                "subscribe": "restricted",
                "unsubscribe": "public",
                "read": "subscribed"
            },
            "objectType": "context"
        }
        return mock_requests_obj(text=json.dumps(context), status_code=200)
    else:
        import ipdb;ipdb.set_trace()
        return mock_requests_obj(text='', status_code=200)


def mock_post(self, *args, **kwargs):  # pragma: no cover
    #Return OK to any post request targeted to 'checktoken', with the mock token
    if args[0].endswith('checktoken'):
        token = kwargs.get('data', {}).get('access_token')
        status_code = 200 if token == MOCK_TOKEN else 401
        return mock_requests_obj(text='', status_code=status_code)
    else:
        return mock_requests_obj(text='', status_code=200)
