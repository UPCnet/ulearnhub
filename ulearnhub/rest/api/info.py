from pyramid.view import view_config
from ulearnhub.rest import endpoint
from ulearnhub.rest import JSONResourceEntity
from ulearnhub.rest import JSONResourceRoot


@view_config(route_name='info', request_method='GET')
@endpoint(authentication=False)
def domains_list(domains, request):

    info = {
        "default_maxserver_url": domains.default_maxserver_url,
        "domains": {}
    }

    for name, domain in domains.items():
        info['domains'][name] = {
            "max_server_url": domain.server
        }
    response = JSONResourceEntity(info)
    return response()
