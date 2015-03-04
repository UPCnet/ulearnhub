# from ulearnhub.models.base import Base
# from sqlalchemy import Integer, Text
# from sqlalchemy import Column
from maxclient.rest import MaxClient

from pyramid.security import Allow
from pyramid.security import Authenticated
from ulearnhub.models.components import COMPONENTS


from persistent.mapping import PersistentMapping


class Domains(PersistentMapping):
    __acl__ = [
        (Allow, Authenticated, 'homepage')
    ]
    __name__ = 'DOMAINS'

    def get_all(self, as_dict=False):
        rows = []
        for row in self.values():
            if as_dict:
                rows.append(row.as_dict())
            else:
                rows.append(row)
        return rows


class Domain(PersistentMapping):

    def __init__(self, name, server):
        """
            Create a domain
        """
        super(Domain, self).__init__()
        self.name = name
        self.server = server

    def as_dict(self):
        di = self.__dict__
        di.pop('data', None)
        return di

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
