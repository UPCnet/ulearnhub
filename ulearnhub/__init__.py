from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid_beaker import session_factory_from_settings, set_cache_regions_from_settings
from ulearnhub.models import DBSession
from ulearnhub.models.base import Base

from .resources import get_root


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # Cache
    set_cache_regions_from_settings(settings)

    # Security & Authentication
    session_factory = session_factory_from_settings(settings)

    authn_policy = AuthTktAuthenticationPolicy('auth_tkt')
    authz_policy = ACLAuthorizationPolicy()

    # Database
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    # App initializaton
    config = Configurator(
        settings=settings,
        root_factory=get_root,
        session_factory=session_factory,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy)

    config.include('pyramid_chameleon')

    # View routes configuration
    config.add_static_view('jquery', 'components/jquery/dist', cache_max_age=3600)
    config.add_static_view('bootstrap', 'components/bootstrap/dist', cache_max_age=3600)
    config.add_static_view('angular', 'components/angular', cache_max_age=3600)
    config.add_static_view('angular-bootstrap', 'components/angular-bootstrap', cache_max_age=3600)
    config.add_static_view('angular-resource', 'components/angular-resource', cache_max_age=3600)
    config.add_static_view('angular-datatables', 'components/angular-datatables/dist', cache_max_age=3600)
    config.add_static_view('datatables', 'components/datatables/media', cache_max_age=3600)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('css', 'css', cache_max_age=3600)
    config.add_static_view('js', 'js', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('domains', '/domains')
    config.add_route('users', '/users')

    config.add_route('api_domain_info', '/api/domains/{domain}/info', traverse='{domain}')
    config.add_route('api_domains', '/api/domains')
    config.scan()

    return config.make_wsgi_app()
