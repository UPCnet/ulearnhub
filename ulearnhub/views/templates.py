from pyramid.security import authenticated_userid
from pyramid.renderers import get_renderer

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
    def domain(self):
        return self.context

    @property
    def masterTemplate(self):
        master = get_renderer('ulearnhub:templates/master.pt').implementation()
        return master

    @property
    def authenticated_user(self):
        return normalize_userdn(authenticated_userid(self.request))

    @property
    def authenticated_user_token(self):
        return self.request.session[self.context.name]['oauth_token']

    @property
    def authenticated_user_domain(self):
        return self.context

    @property
    def authenticated_user_displayname(self):
        return self.request.session.get(self.context.name, {}).get('display_name', self.authenticated_user)

    @property
    def authenticated_user_avatar(self):
        return self.request.session[self.context.name]['avatar']

    @property
    def application_url(self):
        app_url = self.request.application_url
        vh = self.getVirtualHost()
        if vh:
            return vh
        else:
            return app_url

    @property
    def context_url(self):
        try:
            return self.request.resource_url(self.request.context, '').rstrip('/')
        except:
            return self.application_url

    def getVirtualHost(self):
        return self.request.headers.get('X-Virtual-Host-Uri', None)
