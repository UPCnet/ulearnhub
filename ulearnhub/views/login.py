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
from maxclient.client import RequestError
from maxclient.client import BadUsernameOrPasswordError


def real_request_url(request):
    """
        Gets the real request url

        IF a HTTP_X_VIRTUAL_HOST_URI variable is defined, will be used as the
        base url for the request.
    """
    request_scheme = re.search(r'(https?)://', request.url).groups()[0]
    if request.headers.get('HTTP_X_VIRTUAL_HOST_URI'):
        real_scheme = re.search(r'(https?)://', request.get('HTTP_X_VIRTUAL_HOST_URI')).groups()[0]
        return request.url.replace(request_scheme, real_scheme)
    else:
        return request.url


@forbidden_view_config()
def catch_forbidden(context, request):
    """
        Catches forbidden exceptions to redirect to the
        appropiate error page.

        * When forbidden is raised while accessing api endpoint
        (that by convention will be identified by routes prefixed
        with 'api_'), a json error will be rendered.

        * When forbidden is raised while accessing a domain, the
        domain login page will be rendered.

        * Any other forbidden will render the main login view.
    """
    if request.matched_route.name.startswith('api_'):
        return main_forbidden(request)
    elif request.matched_route.name == 'domain':
        return domain_login(context, request)
    else:
        return login(context, request)


def render_response(request, response, template):
    """
        renders a response with the specified template
    """
    if isinstance(response, Response):
        return response

    return Response(render(template, response, request=request))


def login_into_domain(context, request, api, login_response, domain, redirect=''):
    """
        Common login procedure used by both root and domain login views.
    """
    login = request.POST.get('username')
    password = request.POST.get('password')

    if not login or not password or not domain:
        login_response['error'] = 'Missing fields.',
        return login_response

    # Try to authenticate with Osiris, using oauth server from the context
    if domain is None:
        login_response['error'] = 'Unknown domain "{}"'.format(domain.name)
        return login_response

    if not domain.oauth_server:
        login_response['error'] = "Error while contacting with {} oauth server".format(domain.name)
        return login_response

    connector = Connector(request.registry, domain.oauth_server, False)
    try:
        data = connector.authenticate(login, password)
        auth_user, oauth_token = data

        client = domain.maxclient
        client.setActor(auth_user)
        client.setToken(oauth_token)
        user_data = client.people[auth_user].get()
        headers = remember(request, auth_user)

    # if not successful, try again
    except BadUsernameOrPasswordError:
        login_response['error'] = 'Please check your username and password and try again.'
        return login_response

    # Try to get username from max
    try:
        user_data = client.people[auth_user].get()
        user_data.get('displayName', auth_user)
        display_name = user_data.get('displayName', auth_user)
    except RequestError:
        display_name = auth_user

    request.session['root_auth_domain'] = domain.name
    # Store the user's oauth token in the current session domain data
    request.session[domain.name] = dict(
        oauth_token=oauth_token,
        avatar='{}/people/{}/avatar'.format(domain.max_server, auth_user),
        display_name=display_name
    )
    request.session['root'] = request.session[domain.name]

    # Finally, if all went OK
    # return the authenticated view
    return HTTPFound(headers=headers, location=api.application_url + redirect)


@view_config(route_name='login')
def login(context, request):
    """
        Login view prepared to ask for the domain on the login form
    """
    template = 'ulearnhub:templates/login.pt'
    api = TemplateAPI(context, request, "uLearn HUB Login")
    login_url = request.resource_url(request.context, 'login')
    referrer = real_request_url(request)
    if referrer.endswith('login'):
        referrer = api.application_url  # never use the login form itself as came_from

    came_from = request.params.get('came_from', referrer)

    login_response = dict(
        context_url=request.resource_url(request.context, ''),
        url=login_url, came_from=came_from, login='', api=api,
        error=False,
        login_path='login',
        require_domain=True
    )

    if request.params.get('form.submitted', None) is not None:
        # identify
        domain_name = request.POST.get('domain')
        domain = context['domains'].get(domain_name)
        response = login_into_domain(context, request, api, login_response, domain, redirect='')
        return render_response(request, response, template)

    return render_response(request, login_response, template)


@view_config(route_name='domain_login')
def domain_login(context, request):
    """
        Login view prepared to get the domain from the current context
    """

    template = 'ulearnhub:templates/login.pt'
    api = TemplateAPI(context, request, "uLearn HUB Login")
    login_url = request.resource_url(request.context, 'login')
    referrer = real_request_url(request)
    if referrer.endswith('login'):
        referrer = api.application_url  # never use the login form itself as came_from

    came_from = request.params.get('came_from', referrer)

    login_response = dict(
        context_url=request.resource_url(request.context, ''),
        url=login_url, came_from=came_from, login='', api=api,
        error=False,
        login_path='{}/login'.format(request.context.name),
        domain_name=request.context.title,
        require_domain=False
    )

    if request.params.get('form.submitted', None) is not None:
        # identify
        domain = context
        response = login_into_domain(context, request, api, login_response, domain, redirect='/{}'.format(domain.name))
        return render_response(request, response, template)

    return render_response(request, login_response, template)


@view_config(route_name='logout')
def logout(context, request):
    """
        Logs out from root and from every logged in domain
    """
    for domain_name in request.session.keys():
        if not domain_name.startswith('_'):
            request.session.pop(domain_name, None)

    request.session.pop('root_auth_domain', None)
    request.session.pop('root', None)
    headers = forget(request)
    return HTTPFound(location='/', headers=headers)


@view_config(route_name='domain_logout')
def domain_logout(domain, request):
    """
        Logs out from the current domain
    """
    headers = forget(request)
    request.session.pop(domain.name, None)
    return HTTPFound(location=request.resource_url(request.context, ''), headers=headers)
