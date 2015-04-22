from pyramid.view import view_config
from ulearnhub.rest import endpoint
from ulearnhub.rest import JSONResourceEntity
from ulearnhub.security.permissions import set_role


@view_config(route_name='api_users', request_method='POST', permission=set_role)
@endpoint()
def user_add(users, request):
    username = request.json['username']
    domain = request.json['domain']
    roles = request.json['roles']

    user = users.add(username, domain, roles)
    response = JSONResourceEntity(user.as_dict(), status_code=201)
    return response()
