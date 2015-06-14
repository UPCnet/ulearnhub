# -*- coding: utf-8 -*-
from maxclient.rest import MaxClient

from gummanager.libs import LdapServer as GumLdapServer
from persistent.mapping import PersistentMapping
from ulearnhub.models.utils import ConfigWrapper
from ulearnhub.models.utils import RabbitNotifications


class Component(PersistentMapping):
    constrain = []
    desc = 'Component'

    @property
    def type(self):
        return self.__class__.__name__.lower()

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
        ComponentClass = get_component(component_type)
        for component_name, component in self.items():
            matches_component = ComponentClass == component.__class__
            matches_name = True if name is None else component_name == name
            if matches_component and matches_name:
                return component
            else:
                component.get_component(component_type, name=name)

    def as_dict(self):
        obj = {
            'name': self.id,
            'title': self.title,
            'type': self.type,
            'components': [component.as_dict() for component in self.values()]
        }
        return obj


class MaxCluster(Component):
    desc = "Cluster of MAX servers"

    def __init__(self, id, title, config):
        super(MaxCluster, self).__init__(id, title, config)


class MaxServer(Component):
    constrain = MaxCluster
    desc = "MAX server"

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


class OauthServer(Component):
    desc = "Oauth server"

    def __init__(self, id, title, config):
        """
            Create a domain
        """
        super(OauthServer, self).__init__(id, title, config)


class RabbitServer(Component):
    desc = "RabbitMQ Server"

    def __init__(self, id, title, config):
        """
            Create a domain
        """
        super(RabbitServer, self).__init__(id, title, config)

    @property
    def notifications(self):
        return RabbitNotifications(self.config.url)


class LdapServer(Component):
    desc = "LDAP Server"

    def __init__(self, id, title, config):
        """
            Create a LDAP Server
        """
        self.config = config
        self.readonly = self.config.pop('readonly', False)
        self.server = GumLdapServer(ConfigWrapper(self.config))

        super(LdapServer, self).__init__(id, title, config)


class UlearnSite(Component):
    desc = "ULearn instance"

    def __init__(self, id, title, config):
        """
            Create a domain
        """
        super(UlearnSite, self).__init__(id, title, config)


class MongoDBCluster(Component):
    desc = "MongoDB Cluster"

    def __init__(self, id, title, config):
        """
        """
        super(MongoDBCluster, self).__init__(id, title, config)


class StandaloneMongoDBInstance(Component):
    desc = "Standalone MongoDB Instance"

    def __init__(self, id, title, config):
        """
        """
        super(StandaloneMongoDBInstance, self).__init__(id, title, config)


class MongoDBReplicaMember(Component):
    desc = "MongoDB Cluster Member"
    constrain = ''

    def __init__(self, id, title, config):
        """
        """
        super(MongoDBReplicaMember, self).__init__(id, title, config)


def get_component(name_or_class):
    if is_component(name_or_class):
        return name_or_class
    elif isinstance(name_or_class, basestring):
        return get_component_by_name(name_or_class)
    else:
        return None


def get_component_by_name(name):
    return COMPONENTS.get(name, None)


def is_component(klass):
    bases = getattr(klass, '__bases__', [])
    return Component in bases

COMPONENTS = {klass.__name__.lower(): klass for klass in locals().values() if is_component(klass)}
