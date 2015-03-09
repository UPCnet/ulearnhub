from maxclient.rest import MaxClient

from pyramid.security import Allow
from pyramid.security import Authenticated

from persistent.mapping import PersistentMapping
from persistent.list import PersistentList

from gummanager.libs import LdapServer as GumLdapServer


class ConfigWrapper(PersistentMapping):

    @classmethod
    def from_dict(cls, config):
        wrapper = cls()

        def wrap(wvalue):
            if isinstance(wvalue, dict):
                return ConfigWrapper.from_dict(wvalue)
            elif isinstance(wvalue, list):
                wrapped_list = []
                for item in wvalue:
                    wrapped_list.append(wrap(item))
                return wrapped_list
            else:
                return wvalue

        for key, value in config.items():
            wrapped = wrap(value)
            wrapper[key] = wrapped

        return wrapper

    def __getattr__(self, key):
        if self.get(key):
            return self[key]

        else:
            raise AttributeError(key)


class Component(PersistentMapping):
    name = 'component'

    def __repr__(self):
        return '<{} at "{}">'.format(self.__class__.__name__, self.__component_identifier__)

    @property
    def __component_identifier__(self):
        return id(self)

    def set_config(self, config):
        self.config = ConfigWrapper.from_dict(config)


class MaxCluster(Component):
    name = 'maxcluster'

    def __init__(self, title, **config):
        self.title = title
        self.config = config
        self.components = PersistentList()


class MaxServer(Component):

    name = 'maxserver'

    def __init__(self, title, url):
        """
            Create a maxserver
        """
        self.title = title
        self.url = url
        super(MaxServer, self).__init__()

    @property
    def __component_identifier__(self):
        return self.url

    @property
    def maxclient(self):
        client = MaxClient(self.url, self.oauth_server)
        return client

    @property
    def oauth_server(self):
        server_info = MaxClient(self.url).server_info
        return server_info['max.oauth_server']

    def as_dict(self):
        return dict(
            active=self.active,
            url=self.url,
            oauth_server=self.oauth_server
        )


class OauthServer(Component):
    name = 'oauthserver'

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
    name = 'rabbitserver'

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
    name = 'ldapserver'

    def __init__(self, title, readonly=False, config={}):
        """
            Create a domain
        """
        self.readonly = readonly
        self.title = title
        self.set_config(config)

        self.server = GumLdapServer(self.config)

        super(LdapServer, self).__init__()

    def as_dict(self):
        return dict(
            active=self.active,
            url=self.url,
        )


class UlearnSite(Component):
    name = 'ulearnsite'

    __tablename__ = 'ulearnsites'

    def __init__(self, *args, **kwargs):
        """
            Create a domain
        """
        super(UlearnSite, self).__init__(*args, **kwargs)


COMPONENTS = {
    'max': MaxServer,
    'oauth': OauthServer,
    'rabbit': RabbitServer,
    'ldap': LdapServer,
    # 'communities': CommunitiesSite,
    # 'campus': CampusSite,
}
