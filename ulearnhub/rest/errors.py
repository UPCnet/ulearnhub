# -*- coding: utf-8 -*-
from max.MADMax import MADMaxDB
from ulearnhub.rest.exceptions import ConnectionError
from ulearnhub.rest.exceptions import DuplicatedItemError
from ulearnhub.rest.exceptions import Forbidden
from ulearnhub.rest.exceptions import InvalidPermission
from ulearnhub.rest.exceptions import InvalidSearchParams
from ulearnhub.rest.exceptions import JSONHTTPBadRequest
from ulearnhub.rest.exceptions import JSONHTTPForbidden
from ulearnhub.rest.exceptions import JSONHTTPInternalServerError
from ulearnhub.rest.exceptions import JSONHTTPNotFound
from ulearnhub.rest.exceptions import JSONHTTPServiceUnavailable
from ulearnhub.rest.exceptions import JSONHTTPUnauthorized
from ulearnhub.rest.exceptions import MissingField
from ulearnhub.rest.exceptions import ObjectNotFound
from ulearnhub.rest.exceptions import ObjectNotSupported
from ulearnhub.rest.exceptions import Unauthorized
from ulearnhub.rest.exceptions import UnknownUserError
from ulearnhub.rest.exceptions import ValidationError
from max.resources import Root
from max.rest.resources import RESOURCES


from pyramid.settings import asbool

from bson.errors import InvalidId
from datetime import datetime
from hashlib import sha1
from pymongo.errors import AutoReconnect
from pymongo.errors import ConnectionFailure

import json
import logging
import re
import traceback

logger = logging.getLogger('exceptions')
request_logger = logging.getLogger('requestdump')
dump_requests = {'enabled': False}

ERROR_TEMPLATE = """
------------------------------------------------
BEGIN EXCEPTION REPORT: {hash}
DATE: {time}
REQUEST:

{raw_request}

TRACEBACK:

{traceback}

END EXCEPTION REPORT
------------------------------------------------
"""


def format_raw_request(request):
    """
        Formats raw request. Replaces images with a tag to avoid log flood and errors
        returns an error string if not able to parse request
    """
    raw_request = request.as_bytes()
    content_type = request.headers.get('Content-Type', '')
    try:
        if 'multipart/form-data' in content_type:
            boundary = re.search(r"boundary\s*=\s*(.*?)$", content_type).groups()[0]
            if boundary:
                boundary = boundary.replace('$', r'\$')
                image = re.search(r'\r\n(?:.*?Content-type:\s*image.*?)\r\n\r\n(.*?){}'.format(boundary), raw_request, re.DOTALL | re.IGNORECASE).groups()[0]
                if image:
                    raw_request = raw_request.replace(image, '<Image data {} bytes>\r\n'.format(len(image)))

        raw_request.encode('utf-8')

    except UnicodeDecodeError as unicode_error:
        return raw_request[:unicode_error.start] + "\r\n*** Unicode Decode Error parsing request, request trunked at byte {} ***\r\n".format(unicode_error.start)
    except Exception:
        return"\r\n*** Error parsing request ***\r\n\r\n{}\r\n*** End traceback ***".format(traceback.format_exc())

    return raw_request


def format_raw_response(response):
    """
        Formats a raw response. Replaces images with a tag to avoid log flood errors.
        Returns an error string if not able to parse request
    """
    headers = u'\n'.join([u'{}: {}'.format(*header) for header in response.headers.items()])

    has_image = re.search(r'Content-type:\s*image', headers, re.DOTALL | re.IGNORECASE)
    if has_image:
        body = u'<Image data {} bytes>'.format(len(response.body))
    else:
        body = response.ubody

    raw_response = u'{}\n{}\n\n{}'.format(response.status, headers, body)
    return raw_response


def saveException(request, error):  # pragma: no cover
    """
        Logs the exception

        This code will only raise if a non-tested thing appear
         So, as the tests will not ever see this, we exlcude it from coverage
    """
    time = datetime.now().isoformat()

    entry = dict(
        traceback=error,
        time=time,
        raw_request=format_raw_request(request),
        matched_route=request.matched_route.name,
        matchdict=request.matchdict,
    )

    dump = json.dumps(entry)
    entry['hash'] = sha1(dump).hexdigest()
    exception_log = ERROR_TEMPLATE.format(**entry)
    logger.debug(exception_log)
    return entry['hash'], exception_log


def catch_exception(request, e):
    if isinstance(e, ConnectionFailure):
        return JSONHTTPInternalServerError(error=dict(objectType='error', error='DatabaseConnectionError', error_description='Please try again later.'))
    elif isinstance(e, InvalidId):
        return JSONHTTPBadRequest(error=dict(objectType='error', error=InvalidId.__name__, error_description=e.message))
    elif isinstance(e, ObjectNotSupported):
        return JSONHTTPBadRequest(error=dict(objectType='error', error=ObjectNotSupported.__name__, error_description=e.message))
    elif isinstance(e, ObjectNotFound):
        return JSONHTTPNotFound(error=dict(objectType='error', error=ObjectNotFound.__name__, error_description=e.message))
    elif isinstance(e, MissingField):
        return JSONHTTPBadRequest(error=dict(objectType='error', error=MissingField.__name__, error_description=e.message))
    elif isinstance(e, DuplicatedItemError):
        return JSONHTTPBadRequest(error=dict(objectType='error', error=DuplicatedItemError.__name__, error_description=e.message))
    elif isinstance(e, UnknownUserError):
        return JSONHTTPBadRequest(error=dict(objectType='error', error=UnknownUserError.__name__, error_description=e.message))
    elif isinstance(e, Unauthorized):
        return JSONHTTPUnauthorized(error=dict(objectType='error', error=Unauthorized.__name__, error_description=e.message))
    elif isinstance(e, InvalidSearchParams):
        return JSONHTTPBadRequest(error=dict(objectType='error', error=InvalidSearchParams.__name__, error_description=e.message))
    elif isinstance(e, InvalidPermission):
        return JSONHTTPBadRequest(error=dict(objectType='error', error=InvalidPermission.__name__, error_description=e.message))
    elif isinstance(e, ValidationError):
        return JSONHTTPBadRequest(error=dict(objectType='error', error=ValidationError.__name__, error_description=e.message))
    elif isinstance(e, Forbidden):
        return JSONHTTPForbidden(error=dict(objectType='error', error=Forbidden.__name__, error_description=e.message))

    elif isinstance(e, ConnectionError):
        return JSONHTTPServiceUnavailable(error=dict(objectType='error', error=ConnectionError.__name__, error_description=e.message))

    # JSON decode error????
    # elif isinstance(e, ValueError):
    #     return JSONHTTPBadRequest(error=dict(objectType='error', error='JSONDecodeError', error_description='Invalid JSON data found on requests body'))
    # # This code will only raise if a non-tested thing appear
    # So, as the tests will not ever see this, we exlcude it from coverage
    else:  # pragma: no cover
        error = traceback.format_exc()
        sha1_hash, log = saveException(request, error)
        max_server = request.environ.get('HTTP_X_VIRTUAL_HOST_URI', '')

        error_description = 'Your error has been logged at {}/exceptions/{}. Please contact the system admin.'.format(max_server, sha1_hash)
        if asbool(request.registry.settings.get('testing', False)) or asbool(request.registry.settings.get('max.include_traceback_in_500_errors', False)):  # pragma: no cover
            error_description = 'An exception occurred. Below is the catched exception.\n\nSorry for the convenience.\n\n' + log.replace('\n', '\n    ')[:-4]

        return JSONHTTPInternalServerError(error=dict(objectType='error', error='ServerError', error_description=error_description))

SEPARATOR = '-' * 80
DUMP_TEMPLATE = """
{sep}
{{}}

--

{{}}
{sep}
""".format(sep=SEPARATOR)


def dump_request(request, response):
    """
        Logs formatted request + response to request_dump logger
        if global var dump_requests['enabled'] is True
    """
    if dump_requests['enabled'] and response.status_int != 500:
        request_logger.debug(DUMP_TEMPLATE.format(
            format_raw_request(request),
            format_raw_response(response)
        ))


def MaxResponse(fun):
    def replacement(*args, **kwargs):
        """
            Handle exceptions throwed in the process of executing the REST method and
            issue proper status code with message
        """
        nkargs = [a for a in args]
        context, request = isinstance(nkargs[0], Root) and tuple(nkargs) or tuple(nkargs[::-1])
        # response = fun(*args, **kwargs)
        # return response
        try:
            response = fun(*args, **kwargs)
        except AutoReconnect:
            tryin_to_reconnect = True
            while tryin_to_reconnect:
                try:
                    response = fun(*args, **kwargs)
                except AutoReconnect:
                    pass
                except Exception, e:
                    response = catch_exception(request, e)
                    dump_request(request, response)
                    return response
                else:
                    tryin_to_reconnect = False
        except Exception, e:
            response = catch_exception(request, e)
            dump_request(request, response)
            return response
        else:
            # Don't cache by default, get configuration from resource if any
            route_cache_settings = RESOURCES.get(request.matched_route.name, {}).get('cache', 'must-revalidate, max-age=0, no-cache, no-store')
            response.headers.update({'Cache-Control': route_cache_settings})
            dump_request(request, response)
            return response
    replacement.__name__ = fun.__name__
    replacement.__doc__ = fun.__doc__

    return replacement
