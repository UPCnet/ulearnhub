from sqlalchemy import Column
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import Text

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from zope.sqlalchemy import ZopeTransactionExtension
from maxclient.rest import MaxClient

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Domain(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    server = Column(Text)

    @property
    def maxclient(self):
        client = MaxClient(self.server, self.oauth_server)
        return client

    @property
    def oauth_server(self):
        server_info = MaxClient(self.server).server_info
        return server_info['max.oauth_server']

Index('name_index', Domain.name, unique=True, mysql_length=255)
