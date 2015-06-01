# -*- coding: utf-8 -*-
from ulearnhub.resources import root_factory
from ulearnhub.resources import create_defaults
from max.exceptions import Unauthorized
from ulearnhub.routes import ROUTES
from ulearnhub.security.authentication import OauthAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from ulearnhub.security.authentication import MultiDomainAuthTktAuthenticationPolicy
from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from pyramid_beaker import set_cache_regions_from_settings
from pyramid_multiauth import MultiAuthenticationPolicy

import logging
logger = logging.getLogger('ulearnhub')

from max import patches
import json
import os
import re


def get_oauth_headers(request):
    """
        Extracts oauth headers from request
    """
    oauth_token = request.headers.get('X-Oauth-Token', '')
    username = request.headers.get('X-Oauth-Username', '')
    scope = request.headers.get('X-Oauth-Scope', '')

    if not oauth_token or not username:
        # This is for mental sanity in case we miss the body part when writing tests
        if 'X-Oauth-Username' in request.params.keys():
            raise Unauthorized("Authorization found in url params, not in request. Check your tests, you may be passing the authentication headers as the request body...")

        if request.matched_route.name.startswith('api_'):
            raise Unauthorized('No auth headers found.')

    return username.lower(), oauth_token, scope


def get_oauth_domain(request):
    """
        Extracts domain informatin from request
    """
    return request.headers.get('X-Oauth-Domain', None)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # Cache
    set_cache_regions_from_settings(settings)

    # Security & Authentication
    session_factory = session_factory_from_settings(settings)

    authn_policy = MultiAuthenticationPolicy([
        OauthAuthenticationPolicy(allowed_scopes=['widgetcli']),
        MultiDomainAuthTktAuthenticationPolicy('secret')
    ])

    authz_policy = ACLAuthorizationPolicy()

    # Create data folder
    match = re.search(r'file://(.*)/.*$', settings['zodbconn.uri'])
    if match:
        storage_folder = match.groups()[0]
        if not os.path.exists(storage_folder):
            os.makedirs(storage_folder)

    # App initializaton
    config = Configurator(
        settings=settings,
        root_factory=root_factory,
        session_factory=session_factory,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy)

    config.include('pyramid_chameleon')
    config.include("pyramid_zodbconn")

    # View routes configuration
    config.add_static_view('jquery', 'components/jquery/dist', cache_max_age=3600)
    config.add_static_view('bootstrap', 'components/bootstrap/dist', cache_max_age=3600)
    config.add_static_view('templates', 'angular/templates', cache_max_age=3600)
    config.add_static_view('angularjs', 'components/angular', cache_max_age=3600)
    config.add_static_view('ui-utils', 'components/ui-utils', cache_max_age=3600)
    config.add_static_view('maxui', 'maxui', cache_max_age=3600)
    config.add_static_view('prism', 'components/prism', cache_max_age=3600)
    config.add_static_view('angular-ui-router', 'components/angular-ui-router/release', cache_max_age=3600)
    config.add_static_view('angular-bootstrap', 'components/angular-bootstrap', cache_max_age=3600)
    config.add_static_view('angular-resource', 'components/angular-resource', cache_max_age=3600)
    config.add_static_view('angular-datatables', 'components/angular-datatables/dist', cache_max_age=3600)
    config.add_static_view('angular-ui-select', 'components/angular-ui-select/dist', cache_max_age=3600)
    config.add_static_view('angular-sanitize', 'components/angular-sanitize', cache_max_age=3600)
    config.add_static_view('angular-translate', 'components/angular-translate', cache_max_age=3600)
    config.add_static_view('angular-cookies', 'components/angular-cookies', cache_max_age=3600)
    config.add_static_view('angular-translate-static', 'components/angular-translate-loader-static-files', cache_max_age=3600)
    config.add_static_view('angular-elastic-input', 'components/angular-elastic-input/dist', cache_max_age=3600)
    config.add_static_view('angular-slimscroll', 'components/angular-slimscroll', cache_max_age=3600)
    config.add_static_view('angular-markdown', 'components/angular-markdown-directive', cache_max_age=3600)
    config.add_static_view('showdown', 'components/showdown/compressed', cache_max_age=3600)
    config.add_static_view('datatables', 'components/datatables/media', cache_max_age=3600)
    config.add_static_view('underscore', 'components/underscore', cache_max_age=3600)
    config.add_static_view('slimscroll', 'components/slimScroll', cache_max_age=3600)
    config.add_static_view('json-explorer', 'components/ng-json-explorer/dist', cache_max_age=3600)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('css', 'css', cache_max_age=3600)
    config.add_static_view('js', 'js', cache_max_age=3600)
    config.add_static_view('fonts', 'fonts', cache_max_age=3600)
    config.add_static_view('angular', 'angular', cache_max_age=3600)
    config.add_static_view('locales', 'locales', cache_max_age=3600)

    config.add_request_method(get_oauth_headers, name='auth_headers', reify=True)
    config.add_request_method(get_oauth_domain, name='auth_domain', reify=True)

    # REST Resources
    # Configure routes based on resources defined in RESOURCES
    for name, properties in ROUTES.items():
        route_params = {param: value for param, value in properties.items() if param in ['traverse']}
        config.add_route(name, properties.get('route'), **route_params)

    # Test for default structures and initialize them if not found
    defaults_file = settings.get('ulearnhub.defaults', '').strip()
    if os.path.exists(defaults_file):
        defaults = json.loads(open(defaults_file).read())
        create_defaults(config.registry, defaults)

    # Create exceptions log folfer if it doesnt exists
    exceptions_folder = config.registry.settings.get('exceptions_folder')
    if not os.path.exists(exceptions_folder):
        os.makedirs(exceptions_folder)

    config.scan('ulearnhub', ignore=['ulearnhub.tests'])
    config.scan('max.exceptions.views')

    return config.make_wsgi_app()
