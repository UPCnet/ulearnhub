from pyramid.view import view_config
from ulearnhub.rest import endpoint
from ulearnhub.rest import JSONResourceEntity
from ulearnhub.rest import JSONResourceRoot


@view_config(route_name='api_domains', request_method='GET')
@endpoint()
def domains_list(domains, request):
    domains = domains.get_all(as_dict=True)
    response = JSONResourceRoot(domains)
    return response()


@view_config(route_name='api_domains', request_method='POST')
@endpoint()
def domain_add(domains, request):
    new_domain = domains.add_domain(**request.json)
    response = JSONResourceEntity(new_domain.as_dict(), status_code=201)
    return response()


@view_config(route_name='api_domain', request_method='GET')
@endpoint()
def domain(domain, request):
    response = JSONResourceEntity(domain.as_dict())
    return response()
