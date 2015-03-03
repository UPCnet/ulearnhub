from pyramid.view import view_config
from ulearnhub.models import Domain
from ulearnhub.rest import endpoint
from ulearnhub.rest import JSONResourceEntity
from ulearnhub.rest import JSONResourceRoot


@view_config(route_name='api_domains', request_method='GET')
@endpoint()
def domains_list(context, request):
    domains = Domain.get_all(as_dict=True)
    response = JSONResourceRoot(domains)
    return response()


@view_config(route_name='api_domains', request_method='POST')
@endpoint()
def domain_add(context, request):
    new_domain_data = request.json
    response = JSONResourceEntity(new_domain_data)
    return response()
