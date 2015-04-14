from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid_beaker import session_factory_from_settings, set_cache_regions_from_settings

from pyramid_zodbconn import get_connection

import transaction
from persistent.mapping import PersistentMapping
import os
import re
from pyramid.security import Allow
from pyramid.security import Authenticated

class Root(PersistentMapping):
    """
    """
    __name__ = 'ROOT'
    __acl__ = [
        (Allow, Authenticated, 'homepage')
    ]

def bootstrap(zodb_root):
    if 'ulearnhub' not in zodb_root:
        root = Root()
        zodb_root['ulearnhub'] = root
        transaction.commit()

    return zodb_root['ulearnhub']


def domains_factory(request):
    root = root_factory(request)
    return root['domains']


def root_factory(request):
    conn = get_connection(request)
    return bootstrap(conn.root())


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # Cache
    set_cache_regions_from_settings(settings)

    # Security & Authentication
    session_factory = session_factory_from_settings(settings)

    authn_policy = AuthTktAuthenticationPolicy('auth_tkt')
    authz_policy = ACLAuthorizationPolicy()

    # Create data folder
    storage_folder = re.search(r'file://(.*)/.*$', settings['zodbconn.uri'])
    if storage_folder:
        if not os.path.exists(storage_folder.groups()[0]):
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
    config.add_static_view('templates', 'templates/angular', cache_max_age=3600)
    config.add_static_view('angular', 'components/angular', cache_max_age=3600)
    config.add_static_view('angular-ui-router', 'components/angular-ui-router/release', cache_max_age=3600)
    config.add_static_view('angular-bootstrap', 'components/angular-bootstrap', cache_max_age=3600)
    config.add_static_view('angular-resource', 'components/angular-resource', cache_max_age=3600)
    config.add_static_view('angular-datatables', 'components/angular-datatables/dist', cache_max_age=3600)
    config.add_static_view('angular-ui-select', 'components/angular-ui-select/dist', cache_max_age=3600)
    config.add_static_view('angular-sanitize', 'components/angular-sanitize', cache_max_age=3600)
    config.add_static_view('angular-translate', 'components/angular-translate', cache_max_age=3600)
    config.add_static_view('angular-cookies', 'components/angular-cookies', cache_max_age=3600)
    config.add_static_view('angular-translate-static', 'components/angular-translate-loader-static-files', cache_max_age=3600)
    config.add_static_view('datatables', 'components/datatables/media', cache_max_age=3600)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('css', 'css', cache_max_age=3600)
    config.add_static_view('js', 'js', cache_max_age=3600)
    config.add_static_view('locales', 'locales', cache_max_age=3600)

    config.add_route('root', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('domains', '/domains', factory=domains_factory)
    config.add_route('domain', '/domains/{domain}', traverse='/domains/{domain}')

    config.add_route('domain_users', '/domains/{domain}/users', traverse='/domains/{domain}')
    config.add_route('domain_user', '/domains/{domain}/users/{username}', traverse='/domains/{domain}')
    config.add_route('domain_contexts', '/domains/{domain}/contexts', traverse='/domains/{domain}')
    config.add_route('domain_components', '/domains/{domain}/components', traverse='/domains/{domain}')

    config.add_route('initialize', '/initialize')
    config.add_route('api_domain_info', '/api/domains/{domain}/info', traverse='/domains/{domain}')
    config.add_route('api_domains', '/api/domains', factory=domains_factory)
    config.add_route('api_domain', '/api/domains/{domain}', traverse='/domains/{domain}')
    config.scan()

    return config.make_wsgi_app()
