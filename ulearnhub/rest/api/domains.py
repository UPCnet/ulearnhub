from pyramid.view import view_config
from ulearnhub.rest import endpoint
from ulearnhub.rest import JSONResourceEntity
from ulearnhub.rest import JSONResourceRoot
from ulearnhub import deployments_factory
import re


@view_config(route_name='api_domains', request_method='GET')
@endpoint()
def domains_list(domains, request):
    domains = domains.get_all(as_dict=True)
    response = JSONResourceRoot(domains)
    return response()


@view_config(route_name='api_domains', request_method='POST')
@endpoint()
def domain_add(domains, request):
    name = request.json['name']
    title = request.json['title']
    new_domain = domains.add_domain(name, title)
    response = JSONResourceEntity(new_domain.as_dict(), status_code=201)
    return response()


@view_config(route_name='api_domain', request_method='GET')
@endpoint()
def domain(domain, request):
    response = JSONResourceEntity(domain.as_dict())
    return response()


@view_config(route_name='api_domain_components', request_method='POST')
@endpoint()
def domain_assign_component(domain, request):
    component_id = request.json['component_id']
    deployment_name, component_type, component_name = re.match(r'^\s*(.*?)/(.*?):(.*?)\s*$', component_id).groups()

    deployments = deployments_factory(request)
    component = deployments['test'].get_component(component_type, name=component_name)

    domain.assign(component)
    response = JSONResourceEntity(domain.as_dict(), status_code=201)
    return response()
