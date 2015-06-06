# -*- coding: utf-8 -*-
from ulearnhub.security import ROLES, Manager
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
            (Allow, Manager, permissions.add_domain),
            (Allow, Manager, permissions.list_users),
            (Allow, Manager, permissions.set_role),
        ]

    def __init__(self):
        """
            Create a Users permission container
        """
        super(Users, self).__init__()

    def as_list(self):
        entries = []
        for domain, users in self.items():
            for username, user in users.items():
                entry = user.as_dict()
                entry['domain'] = domain
                entries.append(entry)
        return entries

    def add(self, username, domain_name, roles):
        self.setdefault(domain_name, PersistentMapping())
        domain = self[domain_name]
        domain.setdefault(username, User(username, roles))
        user = domain[username]
        user.__parent__ = self
        return user


class User(Persistent):

    def __acl__(self):
        return [
        ]

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
            'roles': [dict(role=role, active=role in self.roles) for role in ROLES]
        }
