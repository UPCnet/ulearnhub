from pyramid.view import view_config
from max.rest import JSONResourceEntity


@view_config(route_name='info', request_method='GET')
def domains_list(domains, request):

    info = {
        "default_maxserver_url": domains.default_maxserver_url,
        "domains": {}
    }

    for name, domain in domains.items():
        info['domains'][name] = {
            "max_server_url": domain.max_server
        }
    response = JSONResourceEntity(request, info)
    return response()
