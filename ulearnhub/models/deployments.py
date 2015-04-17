from persistent.mapping import PersistentMapping
from ulearnhub.models.components import get_component_by_name


class Deployments(PersistentMapping):

    def __init__(self, *args, **kwargs):
        """
            Deployment container
        """
        super(Deployments, self).__init__(*args, **kwargs)
        self.deployments = PersistentMapping()

    def add(self, name, title):
        """
            Adds a new deployment
        """
        if name not in self:
            self[name] = Deployment(name, title)

        return self[name]


class Deployment(PersistentMapping):

    def __init__(self, name, title, *args, **kwargs):
        """
            Create a deployment
        """
        self.name = name
        self.title = title
        super(Deployment, self).__init__(*args, **kwargs)

    def add_component(self, component_type, name, title, params):
        Component = get_component_by_name(component_type)
        new_component = Component(name, title, params)

        if Component.constrain:
            multicomponent = self.get_component(Component.constrain.name)
            multicomponent[name] = new_component
        else:
            self[name] = new_component
        return new_component

    def get_component(self, component_type, name=None):
        for component_name, component in self.items():
            matches_component = component_type == component.__class__.name
            matches_name = True if name is None else component_name == name
            if matches_component and matches_name:
                return component
            else:
                return component.get_component(component_type, name=name)

    def as_dict(self):
        return {
            'name': self.name,
            'title': self.title,
            'components': {component_name: component.as_dict() for component_name, component in self.items()}
        }
