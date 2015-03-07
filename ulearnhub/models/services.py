from ulearnhub.models.components import MaxServer
from ulearnhub.models.components import LdapServer


class Service(object):

    def __init__(self, domain, request):
        self.domain = domain
        self.request = request
        self.data = request.json

    def run(self):
        for component_name in self.target_components:
            handler = self.get_component_handler(component_name)
            handler()
        return {}

    def get_component_handler(self, component_name):
        return getattr(self, 'handle_{}'.format(component_name))

    def noop(self):
        pass


class BatchSubscriber(Service):
    target_components = ['rabbitmq']

    def handle_rabbitmq(self, *args, **kwargs):
        """
            Queues subscription tasks to the domain's rabbitmq broker.

            Format of request as follows:

            {
                "component": {
                    "type": "communities",
                    "id": "url"
                }
                "role_mapping": {
                    "reader": ['read'],
                    "writer": ['read', 'write'],
                    "owner": ['read', 'write']
                },
                "context": "http://(...)",
                "acl": {
                    "groups": [
                        {"id": , "role": ""},
                        ...
                    ]
                    "users": [
                        {"id": , "role": ""},
                    ]
                }
            }
        """

        maxserver = self.domain.get_component(MaxServer)
        ldapserver = self.domain.get_component(LdapServer)

        maxclient = maxserver.maxclient
        username, token = self.request.auth
        maxclient.setActor(username)
        maxclient.setToken(token)

        context = maxclient.contexts[self.data['context']].get()
        subscriptions = maxclient.contexts[self.data['context']].get()

        import ipdb;ipdb.set_trace()
        return {}


SERVICES = {
    'batchsubscriber': BatchSubscriber
}
