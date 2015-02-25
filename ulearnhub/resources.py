from pyramid.security import Allow
from pyramid.security import Authenticated

from ulearnhub.models import DBSession
from ulearnhub.models import Domain

from sqlalchemy.exc import DBAPIError


class Domains(dict):
    __acl__ = [
        (Allow, Authenticated, 'homepage')
    ]
    __name__ = 'DOMAINS'

    def __getitem__(self, key):
        try:
            domain = DBSession.query(Domain).filter(Domain.name == key).first()
        except DBAPIError:
            raise KeyError(key)
        return domain


def get_root(request):
    return Domains()
