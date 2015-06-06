from pyramid.view import view_config
from max.rest import JSONResourceEntity, JSONResourceRoot
from ulearnhub.security import permissions


@view_config(route_name='api_users', request_method='POST', permission=permissions.set_role)
def user_add(users, request):
    username = request.json['username']
    domain = request.json['domain']
    roles = request.json.get('roles', [])

    user = users.add(username, domain, roles)
    response = JSONResourceEntity(request, user.as_dict(), status_code=201)
    return response()


@view_config(route_name='api_users', request_method='GET', permission=permissions.list_users)
def user_list(users, request):
    response = JSONResourceRoot(request, users.as_list(), status_code=200)
    return response()


@view_config(route_name='api_user_role', request_method='DELETE', permission=permissions.set_role)
def user_remove_role(user, request):
    role = request.matchdict['role']
    user.roles.remove(role)
    response = JSONResourceEntity(request, user.as_dict(), status_code=204)
    return response()


@view_config(route_name='api_user_role', request_method='PUT', permission=permissions.set_role)
def user_add_role(user, request):
    role = request.matchdict['role']
    if role not in user.roles:
        user.roles.append(role)
        status = 201
    else:
        status = 200

    response = JSONResourceEntity(request, user.as_dict(), status_code=status)
    return response()
