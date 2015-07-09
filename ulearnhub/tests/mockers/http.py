import httpretty
import json
import re

from ulearnhub.tests import MOCK_TOKEN

TEST_MAXSERVER = 'http://localhost:8081'


# Oauth requests mocks

def http_mock_gettoken():
    httpretty.register_uri(
        httpretty.POST, re.compile(".*?/token"),
        body=json.dumps({"access_token": MOCK_TOKEN}),
        status=200,
        content_type="application/json"
    )


def http_mock_checktoken():
    httpretty.register_uri(
        httpretty.POST, re.compile(".*?/checktoken"),
        body="",
        status=200,
        content_type="application/json"
    )


# MAX requests mocks

def http_mock_user_info():
    info = {
        "username": "test.user",
        "displayName": "Test User"
    }
    httpretty.register_uri(
        httpretty.GET, re.compile("/people/[^\/]+$"),
        body=json.dumps(info),
        status=200,
        content_type="application/json"
    )


def http_mock_info(max_server='http://localhost:8081', oauth_server='https://oauth.upcnet.es'):
    info = {
        "max.oauth_server": oauth_server,
        "version": "4.0.26.dev0",
        "max.server_id": "test"
    }
    httpretty.register_uri(
        httpretty.GET, re.compile("{}/info".format(max_server)),
        body=json.dumps(info),
        status=200,
        content_type="application/json"
    )


def http_mock_get_context(context, uri=TEST_MAXSERVER, status=200):
    httpretty.register_uri(
        httpretty.GET, re.compile("{}/contexts/\w+".format(uri)),
        body=json.dumps(context),
        status=status,
        content_type="application/json"
    )


def http_mock_get_context_subscriptions(subscriptions, uri=TEST_MAXSERVER, status=200):
    httpretty.register_uri(
        httpretty.GET, re.compile("{}/contexts/\w+/subscriptions".format(uri)),
        body=json.dumps(subscriptions),
        status=status,
        content_type="application/json"
    )

# Ulearn communities mocks

TEST_COMMUNITIES_SITE = 'http://test.communities'


def http_mock_group_communities(response, uri=TEST_COMMUNITIES_SITE, status=200):
    httpretty.register_uri(
        httpretty.GET, re.compile('{}/api/groups/\w+/communities'.format(uri)),
        body=json.dumps(response),
        status=status,
        content_type="application/json"
    )
