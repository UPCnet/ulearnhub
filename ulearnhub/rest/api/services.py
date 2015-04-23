from pyramid.view import view_config
from max.rest import JSONResourceEntity

from ulearnhub.security.permissions import execute_service


@view_config(route_name='api_domain_service', request_method='POST', permission=execute_service)
def domain_service(service, request):
    result = service.run(request)
    response = JSONResourceEntity(request, result)
    return response()
