# -*- coding: utf-8 -*-
from pyramid.httpexceptions import HTTPFound

from pyramid.view import view_config
from pyramid.view import forbidden_view_config

from pyramid.security import remember, forget

from pyramid_osiris import Connector
from ulearnhub.views.templates import TemplateAPI
import logging
import re

from ulearnhub.models import DBSession
from ulearnhub.models import Domain
from sqlalchemy.exc import DBAPIError

logger = logging.getLogger('ulearnhub')


def real_request_url(request):
    request_scheme = re.search(r'(https?)://', request.url).groups()[0]
    if request.headers.get('HTTP_X_VIRTUAL_HOST_URI'):
        real_scheme = re.search(r'(https?)://', request.get('HTTP_X_VIRTUAL_HOST_URI')).groups()[0]
        return request.url.replace(request_scheme, real_scheme)
    else:
        return request.url


@view_config(route_name='login', renderer='ulearnhub:templates/login.pt')
@forbidden_view_config(renderer='ulearnhub:templates/login.pt')
def login(request):
    """ The login view - pyramid_ldap enabled with the forbidden view logic.
    """
    page_title = "uLearn HUB Login"
    api = TemplateAPI(request, page_title)
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
        domain = DBSession.query(Domain).filter(Domain.name == domain_name).first()
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
            client.admin.security.roles['HubManager'].users[auth_user].get()
            user_allowed = client.last_response_code == 200

            if user_allowed:
                headers = remember(request, auth_user)
            else:
                login_response['error'] = "You're not allowed to manage this hub."
                return login_response

        # if not successful, try again
        else:
            login_response['error'] = 'Login failed. Please try again.'
            return login_response

        # Store the user's oauth token in the current session
        request.session['oauth_token'] = oauth_token

        # Finally, if all went OK
        # return the authenticated view
        return HTTPFound(headers=headers, location=api.application_url)

    return login_response


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    request.session.pop('oauth_token')
    return HTTPFound(location='/', headers=headers)
