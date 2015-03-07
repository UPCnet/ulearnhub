from maxclient.rest import MaxClient

from pyramid.security import Allow
from pyramid.security import Authenticated
from ulearnhub.models.components import COMPONENTS


from persistent.mapping import PersistentMapping
from persistent.list import PersistentList


class Domains(PersistentMapping):
    __acl__ = [
        (Allow, Authenticated, 'homepage')
    ]
    __name__ = 'DOMAINS'

    def __init__(self):
        """
            Create a domain
        """
        super(Domains, self).__init__()
        self.default_maxserver_url = ''

    def get_all(self, as_dict=False):
        rows = []
        for row in self.values():
            if as_dict:
                rows.append(row.as_dict())
            else:
                rows.append(row)
        return rows

    def add_domain(self, **kwargs):
        domain = Domain(**kwargs)
        return domain


class Domain(PersistentMapping):

    def __init__(self, name, title):
        """
            Create a domain
        """
        super(Domain, self).__init__()
        self.name = name
        self.title = title
        self.components = PersistentList()

    def as_dict(self):
        di = self.__dict__
        di.pop('data', None)
        return di

    def get_component(self, klass):
        for component in self.components:
            if component.__class__ == klass:
                return component
        return None

    @property
    def __acl__(self):
        return [
            (Allow, Authenticated, 'homepage')
        ]

    @property
    def maxclient(self):
        client = MaxClient(self.server, self.oauth_server)
        return client

    def set_token(self, password):
        self.token = self.maxclient.getToken(self.user, password)

    @property
    def oauth_server(self):
        server_info = MaxClient(self.server).server_info
        return server_info['max.oauth_server']

    def add_component(self, component, *args, **kwargs):
        Component = COMPONENTS.get(component)
        new_component = Component(*args, **kwargs)

        self.maxserver = new_component
        return new_component
