from sqlalchemy import create_engine
from ulearnhub.models.base import Base
from ulearnhub.models.domains import Domain
from ulearnhub.models import DBSession

import unittest

ECHO_ON_TEST = False


class UlearnhubTestModels(unittest.TestCase):

    def setUp(self):
        self.engine = create_engine('sqlite://', echo=ECHO_ON_TEST)

        # This line is necessary to guarantee that DB starts empty always
        # I DON'T know why the fuck ...
        DBSession.bind

        DBSession.configure(bind=self.engine)
        self.session = DBSession
        Base.metadata.bind = self.engine
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    def create_domain(self, name):
        domain = Domain(name=name)
        self.session.add(domain)
        return self.get_last(Domain)

    def tearDown(self):
        self.session.flush()
        self.session.close()

    def get_last(self, klass, pos=-1):
        results = self.session.query(klass).all()
        if results:
            return results[pos]
        else:
            return None

    def test_register_domain(self):
        domain = Domain(name="test")
        self.session.add(domain)

        saved_domain = self.get_last(Domain)
        self.assertEqual(saved_domain.name, 'test')

    def test_add_maxserver(self):
        domain = self.create_domain('test')
        domain.add_component('maxserver', url='https://max.upcnet.es')

        self.assertEqual(domain.maxserver.url, 'https://max.upcnet.es')
