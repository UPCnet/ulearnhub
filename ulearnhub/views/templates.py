from pyramid.security import authenticated_userid
from pyramid.renderers import get_renderer
from ulearnhub.security import ROLES
from ulearnhub.models.domains import Domain
from ulearnhub.resources import Root
from collections import namedtuple
from pyramid.settings import asbool
import re


SCRIPTS = {
    'production': [
        'angular-elastic-input/angular-elastic-input.min.js',
        'maxui/maxui.js',
        'js/hub.domain.min.js'
    ],
    'development': [
        'angular-elastic-input/angular-elastic-input.min.js',
        'maxui/maxui.js',
        'angular/hub.domain/hub.domain.module.js',
        'angular/hub.domain/hub.domain.config.js',
        'angular/hub.domain/hub.domain.constants.js',
        'angular/hub.domain/hub.domain.controller.js',
        'angular/hub.domain/endpoints.service.js',
        'angular/hub.domain/endpoints.controller.js',
        'angular/hub.domain/exceptions.controller.js',
        'angular/hub.domain/exception.controller.js',
        'angular/hub.domain/users/users.module.js',
        'angular/hub.domain/users/users.controller.js',
        'angular/hub.domain/users/roles.controller.js',
        'angular/hub.domain/users/modals.controller.js',
        'angular/hub.domain/users/profile.controller.js',
        'angular/hub.domain/contexts/contexts.module.js',
        'angular/hub.domain/contexts/contexts.controller.js',
        'angular/hub.domain/contexts/context.controller.js',
        'angular/hub.domain/contexts/permissions.factory.js',
        'angular/hub.domain/contexts/modals.controller.js',
        'angular/max.client/max.client.module.js',
        'angular/max.client/max.info.js',
        'angular/max.client/max.client.service.js',
        'angular/hub.client/hub.client.module.js',
        'angular/hub.client/hub.client.info.js',
        'angular/hub.client/hub.client.service.js',
        'angular/hub.sidebar/hub.sidebar.module.js',
        'angular/hub.sidebar/hub.sidebar.provider.js',
        'angular/hub.sidebar/hub.sidebar.controller.js'
    ]
}


def normalize_userdn(dn):
    """ Extract user id (e.g. cn=victor.fernandez,ou=Users,dc=upc,dc=edu to
        victor.fernandez, or leave username intact
    """
    if dn:
        regex = r'(cn=)?([^,=]*),?'
        return re.search(regex, dn).groups()[1]
    else:
        return None


class TemplateAPI(object):

    def __init__(self, context, request, page_title=None):
        self.context = context
        self.request = request
        self.error = self.domain_session.pop('error', None)

    @property
    def scripts(self):
        debug_js = asbool(self.request.registry.settings['pyramid.debug_js'])
        mode = 'development' if debug_js else 'production'
        return SCRIPTS[mode]

    @property
    def view(self):
        return self.request.matched_route.name

    @property
    def masterTemplate(self):
        master = get_renderer('ulearnhub:templates/master.pt').implementation()
        return master

    @property
    def angular_name(self):
        if isinstance(self.context, Domain):
            return 'hub.domain'
        elif isinstance(self.context, Root):
            return 'uLearnHUBManagement'

    @property
    def logged_domains(self):
        domains = []
        if isinstance(self.context, Root):
            for domainid in self.request.session.keys():
                if domainid in self.context['domains']:
                    domain = self.context['domains'][domainid]
                    domains.append({
                        "url": self.request.resource_url(domain),
                        "title": domain.title
                    })
        return domains

    @property
    def domain_session(self):
        return self.request.session.get(self.domain['name'], {})

    @property
    def authenticated_user(self):
        hub_roles = set(ROLES).intersection(set(self.request.effective_principals))
        username = normalize_userdn(self.request.authenticated_userid)
        session_domain_data = self.request.session.get(self.domain['name'], {})

        return dict(
            username=username,
            display_name=session_domain_data.get('display_name', username),
            avatar=session_domain_data.get('avatar', ''),
            token=session_domain_data.get('oauth_token', ''),
            role='' if not hub_roles else list(hub_roles)[0]
        )

    @property
    def impersonated(self):
        return 'impersonation' in self.domain_session

    @property
    def impersonated_class(self):
        return 'impersonated' if self.impersonated else ''

    @property
    def impersonated_user(self):
        impersonation = self.domain_session['impersonation']
        impersonated_username = normalize_userdn(impersonation['username'])
        return dict(
            username=impersonated_username,
            display_name=impersonation['display_name'],
            avatar=impersonation['avatar'],
            token=impersonation['token'],
            role='Impersonated'
        )

    @property
    def effective_user(self):
        if self.impersonated:
            return self.impersonated_user
        else:
            return self.authenticated_user

    @property
    def domain(self):
        domain_object = None
        try:
            if isinstance(self.context, Domain):
                domain_object = self.request.context
            elif isinstance(self.context, Root):
                root_auth_domain = self.request.session.get('root_auth_domain')
                domain_object = self.request.context['domains'].get(root_auth_domain, None)

            return dict(
                name=domain_object.name,
                url=self.request.resource_url(domain_object),
                max_server=domain_object.max_server
            )
        except:
            return dict(name='', url='', max_server='')

    def getVirtualHost(self):
        return self.request.headers.get('X-Virtual-Host-Uri', None)

    @property
    def logout_url(self):
        if isinstance(self.context, Domain):
            base = self.domain['url']
        else:
            base = self.application_url
        return '{}/logout'.format(base)

    @property
    def application_url(self):
        app_url = self.request.application_url
        vh = self.getVirtualHost()
        if vh:
            return vh
        else:
            return app_url
