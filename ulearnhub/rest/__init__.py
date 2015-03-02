from pyramid.view import view_config
from ulearnhub.models import Domain


@view_config(route_name='api_domains', request_method='GET', renderer="json")
def domains_list(context, request):
    domains = Domain.get_all(as_dict=True)
    return domains


@view_config(route_name='api_domains', request_method='POST', renderer="json")
def domain_add(context, request):
    import ipdb;ipdb.set_trace()
    domains = Domain.get_all(as_dict=True)
    return domains
