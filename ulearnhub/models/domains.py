from maxclient.rest import MaxClient

from pyramid.security import Allow
from pyramid.security import Authenticated
from ulearnhub.models.components import COMPONENTS
from ulearnhub.security import permissions
from ulearnhub.security import Manager

from persistent.mapping import PersistentMapping
from ulearnhub.models.components import MaxServer


class Domains(PersistentMapping):
    def __acl__(self):
        return [
            (Allow, Authenticated, 'homepage'),
            (Allow, Manager, permissions.list_domains)
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

    def add(self, name, title):
        if name not in self:
            self[name] = Domain(name, title)
            self[name].__parent__ = self
        return self[name]


class Domain(PersistentMapping):

    def __init__(self, name, title):
        """
            Create a domain
        """
        super(Domain, self).__init__()
        self.name = name
        self.title = title

    def as_dict(self):
        di = self.__dict__.copy()
        di.pop('data', None)
        di.pop('__parent__', None)
        di['max'] = self.max_server
        di['oauth'] = self.oauth_server
        return di

    def get_component(self, klass):
        for component_name, component in self.items():
            if isinstance(component, klass):
                return component

    @property
    def __acl__(self):
        return [
            (Allow, Authenticated, 'homepage')
        ]

    @property
    def maxclient(self):
        client = MaxClient(self.max_server, self.oauth_server)
        return client

    def set_token(self, password):
        self.token = self.maxclient.getToken(self.user, password)

    @property
    def max_server(self):
        maxserver = self.get_component(MaxServer)
        return maxserver.config.url if maxserver is not None else maxserver

    @property
    def oauth_server(self):
        if self.max_server:
            server_info = MaxClient(self.max_server).server_info
        else:
            return None

        return server_info.get('max.oauth_server', None)

    def assign(self, component):
        self[component.id] = component
