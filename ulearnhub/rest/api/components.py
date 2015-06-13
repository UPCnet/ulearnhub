from pyramid.view import view_config
from max.rest import JSONResourceRoot
from ulearnhub.security import permissions
from ulearnhub.models.components import COMPONENTS


@view_config(route_name='api_components', request_method='GET', permission=permissions.list_components)
def list_components(deployments, request):
    results = [{'name': name, 'desc': component.desc} for name, component in COMPONENTS.items()]
    response = JSONResourceRoot(request, results)
    return response()
