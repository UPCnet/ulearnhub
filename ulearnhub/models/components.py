from maxclient.rest import MaxClient

from pyramid.security import Allow
from pyramid.security import Authenticated

from persistent.mapping import PersistentMapping


class Component(PersistentMapping):
    name = 'Component'


class MaxServer(Component):

    def __init__(self, *args, **kwargs):
        """
            Create a domain
        """
        super(MaxServer, self).__init__(*args, **kwargs)

    @property
    def maxclient(self):
        client = MaxClient(self.server, self.oauth_server)
        return client

    @property
    def oauth_server(self):
        server_info = MaxClient(self.server).server_info
        return server_info['max.oauth_server']

    def as_dict(self):
        return dict(
            active=self.active,
            server=self.server,
            oauth_server=self.oauth_server
        )


class OauthServer(Component):

    def __init__(self, *args, **kwargs):
        """
            Create a domain
        """
        super(OauthServer, self).__init__(*args, **kwargs)

    def as_dict(self):
        return dict(
            active=self.active,
            url=self.url,
        )


class RabbitServer(Component):
    __tablename__ = 'oauthservers'

    def __init__(self, *args, **kwargs):
        """
            Create a domain
        """
        super(OauthServer, self).__init__(*args, **kwargs)

    def as_dict(self):
        return dict(
            active=self.active,
            url=self.url,
        )


class LdapServer(Component):

    def __init__(self, *args, **kwargs):
        """
            Create a domain
        """
        super(OauthServer, self).__init__(*args, **kwargs)

    def as_dict(self):
        return dict(
            active=self.active,
            url=self.url,
        )


class UlearnSite(Component):
    __tablename__ = 'ulearnsites'

    def __init__(self, *args, **kwargs):
        """
            Create a domain
        """
        super(UlearnSite, self).__init__(*args, **kwargs)


COMPONENTS = {
    'maxserver': MaxServer,
    'ulearnsite': UlearnSite
}
