from pyramid.view import view_config
from max.rest import JSONResourceEntity
from max.rest import JSONResourceRoot
from ulearnhub import root_factory
from ulearnhub.security import permissions
import re


@view_config(route_name='api_domains', request_method='GET', permission=permissions.list_domains)
def domains_list(domains, request):
    domains = domains.get_all(as_dict=True)
    response = JSONResourceRoot(domains)
    return response()


@view_config(route_name='api_domains', request_method='POST', permission=permissions.add_domain)
def domain_add(domains, request):
    name = request.json['name']
    title = request.json['title']
    new_domain = domains.add(name, title)
    response = JSONResourceEntity(request, new_domain.as_dict(), status_code=201)
    return response()


@view_config(route_name='api_domain', request_method='GET', permission=permissions.view_domain)
def domain(domain, request):
    response = JSONResourceEntity(request, domain.as_dict())
    return response()


@view_config(route_name='api_domain_components', request_method='POST', permission=permissions.assign_component)
def domain_assign_component(domain, request):
    component_id = request.json['component_id']
    deployment_name, component_type, component_name = re.match(r'^\s*(.*?)/(.*?):(.*?)\s*$', component_id).groups()

    deployments = root_factory(request)['deployments']
    component = deployments['test'].get_component(component_type, name=component_name)

    domain.assign(component)
    response = JSONResourceEntity(request, domain.as_dict(), status_code=201)
    return response()
