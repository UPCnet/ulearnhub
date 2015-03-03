from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session

from ulearnhub.models import DBSession


class Base(object):

    @classmethod
    def get_session(cls):
        return DBSession

    def _save_consistency_check(self):
        pass

    @property
    def session(self):
        session = None
        try:
            session = Session.object_session(self)
        except:
            pass

        if not session:
            return DBSession
        else:
            return session

    def delete(self):
        self.session.delete(self)

    def save(self):
        self._save_consistency_check()
        self.session.add(self)

    @classmethod
    def get_by_field(cls, field, value):
        query = {field: value}
        instance = cls.get_session().query(cls).filter_by(**query).first()
        if instance:
            instance.session.add(instance)
        return instance

    @classmethod
    def get_by_identifier(cls, value):
        key = getattr(cls, '__identifier__', 'id')
        query = {key: value}
        instance = cls.get_session().query(cls).filter_by(**query).first()
        if instance:
            instance.session.add(instance)
        return instance

    @classmethod
    def get_all(cls, session=None, as_dict=False):
        rows = []
        for row in cls.get_session().query(cls).all():
            if as_dict:
                rows.append(row.as_dict())
            else:
                rows.append(row)
        return rows

Base = declarative_base(cls=Base)
