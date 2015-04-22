from pyramid.security import Allow
from pyramid.security import Authenticated


from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from persistent import Persistent


class Users(PersistentMapping):
    __acl__ = [
        (Allow, Authenticated, 'homepage')
    ]
    __name__ = 'USERS'

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
