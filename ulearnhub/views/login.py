# -*- coding: utf-8 -*-
from pyramid.httpexceptions import HTTPFound

from pyramid.view import view_config
from pyramid.view import forbidden_view_config

from pyramid.security import remember, forget
from max.exceptions.hooks import main_forbidden
from pyramid_osiris import Connector
from ulearnhub.views.templates import TemplateAPI
import re



def real_request_url(request):
    request_scheme = re.search(r'(https?)://', request.url).groups()[0]
    if request.headers.get('HTTP_X_VIRTUAL_HOST_URI'):
        real_scheme = re.search(r'(https?)://', request.get('HTTP_X_VIRTUAL_HOST_URI')).groups()[0]
        return request.url.replace(request_scheme, real_scheme)
    else:
        return request.url


@forbidden_view_config(renderer='ulearnhub:templates/login.pt')
def catch_forbidden(context, request):
    if request.matched_route.name.startswith('api_'):
        return main_forbidden(request)
    else:
        return login(context, request)


@view_config(route_name='login', renderer='ulearnhub:templates/login.pt')
def login(context, request):
    """ The login view - pyramid_ldap enabled with the forbidden view logic.
    """
    api = TemplateAPI(context, request, "uLearn HUB Login")
    login_url = request.resource_url(request.context, 'login')
    referrer = real_request_url(request)
    if referrer.endswith('login'):
        referrer = api.application_url  # never use the login form itself as came_from

    came_from = request.params.get('came_from', referrer)
    login = ''
    password = ''

    login_response = dict(
        context_url=request.resource_url(request.context, ''),
        url=login_url, came_from=came_from, login=login, api=api,
        error=False
    )

    if request.params.get('form.submitted', None) is not None:
        # identify
        login = request.POST.get('username')
        domain_name = request.POST.get('domain')
        password = request.POST.get('password')

        if not login or not password or not domain_name:
            login_response['error'] = 'You need to suply an username, domain and password.',
            return login_response

        # Try to authenticate with Osiris, using oauth server from the context
        domain = context['domains'][domain_name]
        if domain is None:
            login_response['error'] = "Domain {} is not registered or doesn't exist".format(domain_name)
            return login_response

        if not domain.oauth_server:
            login_response['error'] = "Error while authenticating with {} oauth server".format(domain_name)
            return login_response

        connector = Connector(request.registry, domain.oauth_server, False)
        data = connector.authenticate(login, password)
        if data:
            auth_user, oauth_token = data

            client = domain.maxclient
            client.setActor(auth_user)
            client.setToken(oauth_token)
            user_data = client.people[auth_user].get()
            headers = remember(request, auth_user)

        # if not successful, try again
        else:
            login_response['error'] = 'Login failed. Please try again.'
            return login_response

        # Store the user's oauth token in the current session
        request.session['domain'] = domain.name
        request.session['oauth_token'] = oauth_token
        request.session['display_name'] = user_data.get('displayName', auth_user)
        request.session['avatar'] = '{}/people/{}/avatar'.format(domain.max_server, auth_user)

        # Finally, if all went OK
        # return the authenticated view
        return HTTPFound(headers=headers, location=api.application_url)

    return login_response


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    request.session.pop('oauth_token')
    request.session.pop('display_name')
    request.session.pop('avatar')
    request.session.pop('domain')
    return HTTPFound(location='/', headers=headers)
