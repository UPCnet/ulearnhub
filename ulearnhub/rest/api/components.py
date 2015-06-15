from pyramid.view import view_config
from max.rest import JSONResourceRoot
from ulearnhub.security import permissions
from ulearnhub.models.components import COMPONENTS


@view_config(route_name='api_components', request_method='GET', permission=permissions.list_components)
def list_components(deployments, request):

    def get_spec(component):
        return {
            'type': component.type,
            'desc': component.desc,
            'components': [],
        }

    results = []
    aggregable = {}
    for typename, component in COMPONENTS.items():
        component_spec = get_spec(component)
        component_spec['aggregable'] = component.aggregable.type if component.aggregable else None
        results.append(component_spec)
        if component.aggregable:
            aggregable.setdefault(component.aggregable.type, [])
            aggregable[component.aggregable.type].append(get_spec(component))

    for result in results:
        if result['type'] in aggregable:
            result['components'] = aggregable[result['type']]
        del result['aggregable']

    response = JSONResourceRoot(request, results)
    return response()
