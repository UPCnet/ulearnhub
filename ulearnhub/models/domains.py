# -*- coding: utf-8 -*-
from maxclient.rest import MaxClient

from ulearnhub.models.components import MaxServer
from ulearnhub.models.services import ServicesContainer
from ulearnhub.security import Manager
from ulearnhub.security import permissions

from pyramid.security import Allow

from persistent.mapping import PersistentMapping


class Domains(PersistentMapping):

    __name__ = 'DOMAINS'

    @property
    def __acl__(self):
        return [
            (Allow, Manager, permissions.list_domains),
            (Allow, Manager, permissions.add_domain)
        ]

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

    __name__ = 'DOMAIN'

    def __resource_url__(self, request, info):
        app_url = request.headers.get('X-Virtual-Host-Uri', request.application_url).rstrip('/')
        return '/'.join((app_url, self.name))

    @property
    def __acl__(self):
        return [
            (Allow, Manager, permissions.view_domain),
            (Allow, Manager, permissions.assign_component)
        ]

    @property
    def maxclient(self):
        client = MaxClient(self.max_server, self.oauth_server)
        return client

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

    def __init__(self, name, title):
        """
            Create a domain
        """
        super(Domain, self).__init__()
        self.name = name
        self.title = title
        self['services'] = ServicesContainer(self)

    def as_dict(self):
        di = self.__dict__.copy()
        di.pop('data', None)
        di.pop('__parent__', None)
        di.pop('services', None)
        di['max'] = self.max_server
        di['oauth'] = self.oauth_server
        return di

    def get_component(self, klass):
        for component_name, component in self.items():
            if isinstance(component, klass):
                return component

    def set_token(self, password):
        self.token = self.maxclient.getToken(self.user, password)

    def assign(self, component):
        self[component.id] = component
