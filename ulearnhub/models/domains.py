from ulearnhub.models.base import Base
from sqlalchemy import Integer, Text
from sqlalchemy import Column

from maxclient.rest import MaxClient


class Domain(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    server = Column(Text)
    user = Column(Text)
    token = Column(Text)

    def __init__(self, *args, **kwargs):
        """
            Create a rallie with a predefined average speed group.
        """
        password = kwargs.pop('password', None)
        super(Domain, self).__init__(*args, **kwargs)
        self.set_token(password)

    def set_token(self, password):
        self.token = self.maxclient.getToken(self.user, password)

    @property
    def maxclient(self):
        client = MaxClient(self.server, self.oauth_server)
        return client

    @property
    def oauth_server(self):
        server_info = MaxClient(self.server).server_info
        return server_info['max.oauth_server']

    def as_dict(self):
        return dict(
            name=self.name,
            server=self.server,
            user=self.user,
            token=self.token,
            oauth_server=self.oauth_server
        )
