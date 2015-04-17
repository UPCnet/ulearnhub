from pyramid.view import view_config
from ulearnhub.rest import endpoint
from ulearnhub.rest import JSONResourceEntity
from ulearnhub.rest import JSONResourceRoot


@view_config(route_name='api_deployments', request_method='POST')
@endpoint()
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

    response = JSONResourceEntity(deployment.as_dict(), status_code=status_code)
    return response()


@view_config(route_name='api_deployment', request_method='GET')
@endpoint()
def get_deployment(deployment, request):
    """
        Gets an existing deployment.
    """
    response = JSONResourceEntity(deployment.as_dict(), status_code=200)
    return response()


@view_config(route_name='api_deployment_components', request_method='POST')
@endpoint()
def add_component(deployment, request):
    component_type = request.json['component']
    name = request.json['name']
    title = request.json['title']
    params = request.json['params']
    component = deployment.add_component(component_type, name, title, params)
    response = JSONResourceEntity(component.as_dict(), status_code=201)
    return response()

