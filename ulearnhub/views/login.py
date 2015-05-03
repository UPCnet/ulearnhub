# -*- coding: utf-8 -*-
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.view import forbidden_view_config

from pyramid.security import remember, forget
from max.exceptions.hooks import main_forbidden
from pyramid_osiris import Connector
from ulearnhub.views.templates import TemplateAPI
import re
from pyramid.renderers import render


def real_request_url(request):
    request_scheme = re.search(r'(https?)://', request.url).groups()[0]
    if request.headers.get('HTTP_X_VIRTUAL_HOST_URI'):
        real_scheme = re.search(r'(https?)://', request.get('HTTP_X_VIRTUAL_HOST_URI')).groups()[0]
        return request.url.replace(request_scheme, real_scheme)
    else:
        return request.url


@forbidden_view_config()
def catch_forbidden(context, request):
    if request.matched_route.name.startswith('api_'):
        return main_forbidden(request)
    elif request.matched_route.name == 'domain':
        return domain_login(context, request)
    else:
        return login(context, request)


def render_response(request, response, template):
    return Response(render(template, response, request=request))


@view_config(route_name='login')
def login(context, request):
    """ The login view - pyramid_ldap enabled with the forbidden view logic.
    """
    template = 'ulearnhub:templates/login.pt'
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
            return render_response(request, login_response, template)

        # Try to authenticate with Osiris, using oauth server from the context
        domain = context['domains'][domain_name]
        if domain is None:
            login_response['error'] = "Domain {} is not registered or doesn't exist".format(domain_name)
            return render_response(request, login_response, template)

        if not domain.oauth_server:
            login_response['error'] = "Error while authenticating with {} oauth server".format(domain_name)
            return render_response(request, login_response, template)

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
            return render_response(request, login_response, template)

        # Store the user's oauth token in the current session
        request.session['domain'] = domain.name
        request.session['oauth_token'] = oauth_token
        request.session['display_name'] = user_data.get('displayName', auth_user)
        request.session['avatar'] = '{}/people/{}/avatar'.format(domain.max_server, auth_user)

        # Finally, if all went OK
        # return the authenticated view
        return HTTPFound(headers=headers, location=api.application_url)

    return render_response(request, login_response, template)


@view_config(route_name='domain_login')
def domain_login(context, request):
    """ The login view - pyramid_ldap enabled with the forbidden view logic.
    """
    template = 'ulearnhub:templates/domain_login.pt'
    api = TemplateAPI(context, request, "uLearn HUB Login")
    login_url = request.resource_url(request.context, 'login')
    context_url = request.resource_url(request.context, '')
    referrer = real_request_url(request)
    if referrer.endswith('login'):
        referrer = api.application_url  # never use the login form itself as came_from

    came_from = request.params.get('came_from', referrer)
    login = ''
    password = ''

    login_response = dict(
        context_url=context_url,
        url=login_url, came_from=came_from, login=login, api=api,
        error=False
    )

    if request.params.get('form.submitted', None) is not None:
        # identify
        login = request.POST.get('username')
        password = request.POST.get('password')

        if not login or not password:
            login_response['error'] = 'You need to suply an username, and password.',
            return render_response(request, login_response, template)

        # Try to authenticate with Osiris, using oauth server from the context
        domain = context

        if not domain.oauth_server:
            login_response['error'] = "Error while authenticating with {} oauth server".format(domain.name)
            return render_response(request, login_response, template)

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
            return render_response(request, login_response, template)

        # Store the user's oauth token in the current session
        request.session['domain'] = domain.name
        request.session['oauth_token'] = oauth_token
        request.session['display_name'] = user_data.get('displayName', auth_user)
        request.session['avatar'] = '{}/people/{}/avatar'.format(domain.max_server, auth_user)

        # Finally, if all went OK
        # return the authenticated view
        return HTTPFound(headers=headers, location=context_url)

    return render_response(request, login_response, template)


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    request.session.pop('oauth_token')
    request.session.pop('display_name')
    request.session.pop('avatar')
    request.session.pop('domain')
    return HTTPFound(location='/', headers=headers)
