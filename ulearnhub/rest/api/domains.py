from pyramid.view import view_config
from ulearnhub.rest import endpoint
from ulearnhub.rest import JSONResourceEntity
from ulearnhub.rest import JSONResourceRoot


@view_config(route_name='api_domains', request_method='GET')
@endpoint()
def domains_list(domain_root, request):
    domains = domain_root.get_all(as_dict=True)
    response = JSONResourceRoot(domains)
    return response()


@view_config(route_name='api_domains', request_method='POST')
@endpoint()
def domain_add(context, request):
    new_domain = Domain(**request.json)
    new_domain.save()
    response = JSONResourceEntity(new_domain.as_dict())
    return response()


@view_config(route_name='api_domain', request_method='GET')
@endpoint()
def domain(domain, request):
    response = JSONResourceEntity(domain.as_dict())
    return response
