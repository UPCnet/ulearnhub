from pyramid.view import view_config
from ulearnhub.rest import endpoint
from ulearnhub.rest import JSONResourceEntity

from ulearnhub.models.services import SERVICES


@view_config(route_name='api_domain_service', request_method='POST')
@endpoint()
def domain_service(domain, request):
    Service = SERVICES[request.matchdict['service']]
    service = Service(domain, request)
    result = service.run()

    response = JSONResourceEntity(result)
    return response()
