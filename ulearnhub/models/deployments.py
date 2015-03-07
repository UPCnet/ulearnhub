from persistent.list import PersistentList
from persistent.mapping import PersistentMapping


class Deployments(PersistentMapping):

    def __init__(self, *args, **kwargs):
        """
            Create a deployment
        """
        super(Deployments, self).__init__(*args, **kwargs)
        self.deployments = PersistentMapping()


class Deployment(PersistentMapping):

    def __init__(self, name, title, *args, **kwargs):
        """
            Create a deployment
        """
        self.name = name
        self.title = title
        self.components = PersistentList()
        super(Deployment, self).__init__(*args, **kwargs)


