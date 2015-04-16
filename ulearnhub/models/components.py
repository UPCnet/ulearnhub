from maxclient.rest import MaxClient

from pyramid.security import Allow
from pyramid.security import Authenticated

from persistent.mapping import PersistentMapping
from persistent.list import PersistentList

from gummanager.libs import LdapServer as GumLdapServer

import pkg_resources

from maxcarrot import RabbitClient
from maxcarrot import RabbitMessage
from socket import error as socket_error

import sys
import json

from ulearnhub.rest.exceptions import ConnectionError


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

    def __init__(self, name, url):
        """
            Create a domain
        """
        self.name = name
        self.url = url
        super(RabbitServer, self).__init__()

    @property
    def notifications(self):
        return RabbitNotifications(self.url)

    def as_dict(self):
        return dict(
            active=self.active,
            url=self.url,
        )


def noop(*args, **kwargs):
    """
        Dummy method executed in replacement of the requested method
        when rabbitmq is not defined (i.e. in tests)
    """
    pass


class RabbitNotifications(object):
    """
        Wrapper to access notification methods, and catch possible exceptions
    """

    def __init__(self, url):
        self.url = url
        self.message_defaults = {
            "source": "hub",
            "version": pkg_resources.require("ulearnhub")[0].version,
        }

        client_properties = {
            "product": "hub",
            "version": pkg_resources.require("ulearnhub")[0].version,
            "platform": 'Python {0.major}.{0.minor}.{0.micro}'.format(sys.version_info),
        }
        self.enabled = True

        try:
            self.client = RabbitClient(self.url, client_properties=client_properties)
        except AttributeError:
            self.enabled = False
        except socket_error:
            raise ConnectionError("Could not connect to rabbitmq broker")

    def sync_acl(self, domain, context, username, tasks):
        """
            Sends a Carrot (TM) notification of a new sync acl task
        """
        # Send a conversation creation notification to rabbit
        message = RabbitMessage()
        message.prepare(self.message_defaults)
        message.update({
            "user": {
                'username': username,
            },
            "domain": domain,
            "action": "modify",
            "object": "context",
            "data": {'context': context,
                     'tasks': tasks}
        })
        self.client.send(
            'syncacl',
            json.dumps(message.packed),
            routing_key='')


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


COMPONENTS = {klass.name: klass for klass in locals().values() if Component in getattr(klass, '__bases__', [])}
