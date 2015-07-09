from pyramid.view import view_config
from max.rest import JSONResourceEntity

from ulearnhub.security.permissions import execute_service


@view_config(route_name='api_domain_service', request_method='POST', permission=execute_service)
def domain_service(domain, request):
    service = domain.services[request.matchdict['service']]
    result = service.run(request)
    response = JSONResourceEntity(request, result)
    return response()


@view_config(route_name='api_deployment_component_service', request_method='POST', permission=execute_service)
def component_service(component, request):
    service = component.services[request.matchdict['service']]
    result = service.run(request)
    response = JSONResourceEntity(request, result)
    return response()
