from pyramid.response import Response
from pyramid.view import view_config


@view_config(route_name='api_domain_info')
def domain_info(domain, request):
    return Response(domain.server)
