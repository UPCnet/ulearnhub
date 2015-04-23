# -*- coding: utf-8 -*-
from ulearnhub.security import Manager
from ulearnhub.security import permissions

from pyramid.security import Allow

from persistent import Persistent
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping


class Users(PersistentMapping):

    __name__ = 'USERS'

    @property
    def __acl__(self):
        return [
            (Allow, Manager, permissions.list_domains),
            (Allow, Manager, permissions.add_domain)
        ]

    def __init__(self):
        """
            Create a Users permission container
        """
        super(Users, self).__init__()

    def add(self, username, domain_name, roles):
        self.setdefault(domain_name, PersistentMapping())
        domain = self[domain_name]
        domain.setdefault(username, User(username, roles))
        user = domain[username]
        return user


class User(Persistent):

    def __init__(self, username, roles):
        """
            Create a User entry
        """
        super(User, self).__init__()
        self.username = username
        self.set_roles(roles)

    def set_roles(self, roles):
        self.roles = PersistentList()
        self.roles.extend(roles)

    def as_dict(self):
        return {
            'username': self.username,
            'domain': self.domain,
            'roles': list(self.roles)
        }
