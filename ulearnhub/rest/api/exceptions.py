from pyramid.view import view_config
from max.rest import JSONResourceEntity
from max.rest import JSONResourceRoot
from max.exceptions import ObjectNotFound
from ulearnhub.security import permissions
import re
import glob
import os
from datetime import datetime
from pyramid.httpexceptions import HTTPNoContent


@view_config(route_name='api_exception', request_method='GET', permission=permissions.manage_exceptions)
def getException(context, request):
    """
        Get an exception
    """
    ehash = request.matchdict['hash']
    exceptions_folder = request.registry.settings.get('exceptions_folder')
    matches = glob.glob('{}/*{}'.format(exceptions_folder, ehash))

    if not matches:
        raise ObjectNotFound("There is no logged exception with this hash")

    exception = open(matches[0]).read()
    regex = r'BEGIN EXCEPTION REPORT: .*?\nDATE: (.*?)\nREQUEST:\n\n(.*?)\n\nTRACEBACK:\n\n(.*?)\nEND EXCEPTION REPORT'
    match = re.search(regex, exception, re.DOTALL)

    date, http_request, traceback = match.groups()

    result = {
        'date': date,
        'request': http_request,
        'traceback': traceback
    }
    response = JSONResourceEntity(request, result)
    return response()


@view_config(route_name='api_exception', request_method='DELETE', permission=permissions.manage_exceptions)
def deleteException(context, request):
    """
        Delete an exception
    """
    ehash = request.matchdict['hash']
    exceptions_folder = request.registry.settings.get('exceptions_folder')
    matches = glob.glob('{}/*{}'.format(exceptions_folder, ehash))

    if not matches:
        raise ObjectNotFound("There is no logged exception with this hash")

    os.remove(matches[0])
    return HTTPNoContent()


@view_config(route_name='api_exceptions', request_method='GET', permission=permissions.manage_exceptions)
def getExceptions(context, request):
    """
        Get all exceptions
    """
    exceptions_folder = request.registry.settings.get('exceptions_folder')
    exception_files = os.listdir(exceptions_folder)

    def get_exceptions():
        for exception_filename in exception_files:
            try:
                logger, date, exception_id = exception_filename.split('_')
            except:
                pass

            yield {
                'id': exception_id,
                'date': datetime.strptime(date, '%Y%m%d%H%M%S').strftime('%Y/%m/%d %H:%M:%S')
            }

    response = JSONResourceRoot(request, sorted(get_exceptions(), key=lambda x: x['date'], reverse=True))
    return response()
