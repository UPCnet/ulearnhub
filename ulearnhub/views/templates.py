from pyramid.security import authenticated_userid
from pyramid.renderers import get_renderer
from ulearnhub.security import ROLES
from ulearnhub.models.domains import Domain
from ulearnhub.resources import Root
import re


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
            return 'uLearnHUBDomainManagement'
        elif isinstance(self.context, Root):
            return 'uLearnHUBManagement'

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
        if isinstance(self.context, Domain):
            domain_object = self.request.context
        elif isinstance(self.context, Root):
            domain_object = self.request.context['domains'][self.request.session['root_auth_domain']]

        else:
            return {'name': '', 'url': '', 'max_server': ''}

        return dict(
            name=domain_object.name,
            url=self.request.resource_url(domain_object),
            max_server=domain_object.max_server
        )

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
