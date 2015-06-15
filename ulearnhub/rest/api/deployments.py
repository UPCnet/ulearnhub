from pyramid.view import view_config
from max.rest import JSONResourceEntity
from ulearnhub.security import permissions
from ulearnhub.models.components import get_component


@view_config(route_name='api_deployments', request_method='POST', permission=permissions.add_deployment)
def add_deployment(deployments, request):
    """
        Adds a new deployment.

        {
            "name": "deployment_id",
            "title": "Deployment Title"
        }
    """
    params = request.json
    name = params['name']
    title = params['title']

    if params['name'] in deployments:
        status_code = 200
        deployment = deployments[name]
    else:
        status_code = 201
        deployment = deployments.add(name, title)

    response = JSONResourceEntity(request, deployment.as_dict(), status_code=status_code)
    return response()


@view_config(route_name='api_deployment', request_method='GET', permission=permissions.view_deployment)
def get_deployment(deployment, request):
    """
        Gets an existing deployment.
    """
    deployment = deployment.as_dict()
    response = JSONResourceEntity(request, deployment, status_code=200)
    return response()


@view_config(route_name='api_deployments', request_method='GET', permission=permissions.list_deployments)
def list_deployments(deployments, request):
    response = JSONResourceEntity(request, deployments.as_list(), status_code=200)
    return response()


@view_config(route_name='api_deployment_components', request_method='POST', permission=permissions.add_component)
def add_component(deployment, request):
    """
        Add a component to an existing deployment

        A new component of type specified in "component" field will be added to
        the deployment. If the parent field is given, an existing component will be searched
        and the new component will be added as a child.

        Type of the parent component will be determined by the aggregable attribute of the
        component type we're adding, so if no component named as requested and with the correct type
        is found, the component won't be added.
    """
    component_type = request.json['component']
    name = request.json['name']
    title = request.json['title']
    params = request.json['params']
    parent = request.json.get('parent', None)

    if parent:
        component_spec = get_component(component_type)
        if component_spec.aggregable:
            parent_component = deployment.get_component(component_spec.aggregable.type, name=parent)
    else:
        parent_component = None

    component = deployment.add_component(component_type, name, title, params, parent_component=parent_component)
    response = JSONResourceEntity(request, component.as_dict(), status_code=201)
    return response()
