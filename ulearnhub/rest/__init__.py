# -*- coding: utf-8 -*-
from pyramid.response import Response
from ulearnhub.rest.authentication import authenticate
from ulearnhub.rest.errors import catch_exception
from ulearnhub.rest.errors import dump_request
import json

DEFAULT_ALLOWED_SCOPES = ['widgetcli']


def endpoint(allowed_scopes=DEFAULT_ALLOWED_SCOPES, authentication=False):
    def wrap(view_function):
        def replacement(context, request, *args, **kwargs):
            try:
                if authentication:
                    authenticate(request, allowed_scopes)
                result = view_function(context, request, *args, **kwargs)
                return result
            except Exception, e:
                response = catch_exception(request, e)
                dump_request(request, response)
                return response
            else:
                # Don't cache by default, get configuration from resource if any
                route_cache_settings = 'must-revalidate, max-age=0, no-cache, no-store'
                response.headers.update({'Cache-Control': route_cache_settings})
                dump_request(request, response)
                return response

        replacement.__doc__ = view_function.__doc__
        replacement.__name__ = view_function.__name__
        return replacement
    return wrap


class JSONResourceRoot(object):
    """
    """
    response_content_type = 'application/json'

    def __init__(self, data, status_code=200, stats=False, remaining=False):
        """
        """
        self.data = data
        self.status_code = status_code
        self.stats = stats
        self.remaining = remaining
        self.headers = {}

    def wrap(self):
        """
        """
        wrapper = self.data
        return wrapper

    def __call__(self, payload=None):
        """
            Translate to JSON object if any data. If data is not a list
            something went wrong
        """

        if self.stats:
            response_payload = ''
            self.headers['X-totalItems'] = str(self.data)
        else:
            response_payload = json.dumps(self.wrap())

        if self.remaining:
            self.headers['X-Has-Remaining-Items'] = '1'

        data = response_payload is None and self.data or response_payload
        response = Response(data, status_int=self.status_code)
        response.content_type = self.response_content_type
        for key, value in self.headers.items():
            response.headers.add(key, value)
        return response


class JSONResourceEntity(object):
    """
    """
    response_content_type = 'application/json'

    def __init__(self, data, status_code=200):
        """
        """
        self.data = data
        self.status_code = status_code

    def __call__(self, payload=None):
        """
            Translate to JSON object if any data. If data is not a dict,
            something went wrong
        """
        response_payload = json.dumps(self.data)

        data = response_payload is None and self.data or response_payload
        response = Response(data, status_int=self.status_code)
        response.content_type = self.response_content_type

        return response
