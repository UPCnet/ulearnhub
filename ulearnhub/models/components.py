# -*- coding: utf-8 -*-
from maxclient.rest import MaxClient

from gummanager.libs import LdapServer as GumLdapServer
from persistent.mapping import PersistentMapping
from ulearnhub.models.utils import ConfigWrapper
from ulearnhub.models.utils import RabbitNotifications


class Component(PersistentMapping):
    name = 'component'
    constrain = []

    def __repr__(self):
        return '<{} at "{}">'.format(self.__class__.__name__, self.__component_identifier__)

    @property
    def __component_identifier__(self):
        return id(self)

    def set_config(self, config):
        self.config = ConfigWrapper.from_dict(config)

    def __init__(self, id, title, config):
        PersistentMapping.__init__(self)
        self.title = title
        self.id = id
        self.set_config(config)

    def get_component(self, component_type, name=None):
        for component_name, component in self.items():
            matches_component = component_type == component.__class__.name
            matches_name = True if name is None else component_name == name
            if matches_component and matches_name:
                return component
            else:
                component.get_component(component_type, name=name)


class MaxCluster(Component):
    name = 'maxcluster'

    def __init__(self, id, title, config):
        super(MaxCluster, self).__init__(id, title, config)

    def as_dict(self):
        return dict(
            server=self.config.server,
            components={component_name: component.as_dict() for component_name, component in self.items()}
        )


class MaxServer(Component):
    name = 'maxserver'
    constrain = MaxCluster

    def __init__(self, id, title, config):
        """
            Create a maxserver
        """
        super(MaxServer, self).__init__(id, title, config)

    @property
    def __component_identifier__(self):
        return self.config.url

    @property
    def maxclient(self):
        client = MaxClient(self.config.url, self.oauth_server)
        return client

    @property
    def oauth_server(self):
        server_info = MaxClient(self.config.url).server_info
        return server_info['max.oauth_server']

    def as_dict(self):
        return dict(
            url=self.config.url,
            oauth_server=self.oauth_server,
        )


class OauthServer(Component):
    name = 'oauthserver'

    def __init__(self, id, title, config):
        """
            Create a domain
        """
        super(OauthServer, self).__init__(id, title, config)

    def as_dict(self):
        return dict(
            url=self.config.url,
        )


class RabbitServer(Component):
    name = 'rabbitserver'

    def __init__(self, id, title, config):
        """
            Create a domain
        """
        super(RabbitServer, self).__init__(id, title, config)

    @property
    def notifications(self):
        return RabbitNotifications(self.config.url)

    def as_dict(self):
        return dict(
            url=self.config.url,
        )


class LdapServer(Component):
    name = 'ldapserver'

    def __init__(self, id, title, config):
        """
            Create a domain
        """
        self.readonly = config.pop('readonly', False)
        super(LdapServer, self).__init__(id, title, config)
        self.server = GumLdapServer(self.config)

    def as_dict(self):
        return dict(
            server=self.config.server,
        )


class UlearnSite(Component):
    name = 'ulearnsite'

    __tablename__ = 'ulearnsites'

    def __init__(self, id, title, config):
        """
            Create a domain
        """
        super(UlearnSite, self).__init__(id, title, config)


def get_component_by_name(name):
    return COMPONENTS.get(name, None)


def is_component(klass):
    bases = getattr(klass, '__bases__', [])
    return Component in bases

COMPONENTS = {klass.name: klass for klass in locals().values() if is_component(klass)}
