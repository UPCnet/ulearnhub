# -*- coding: utf-8 -*-
from ulearnhub.models.components import get_component_by_name
from ulearnhub.security import Manager
from ulearnhub.security import permissions

from pyramid.security import Allow

from persistent.mapping import PersistentMapping


class Deployments(PersistentMapping):

    __name__ = 'DEPLOYMENTS'

    @property
    def __acl__(self):
        return [
            (Allow, Manager, permissions.list_deployments),
            (Allow, Manager, permissions.add_deployment)
        ]

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
            self[name].__parent__ = self

        return self[name]


class Deployment(PersistentMapping):

    __name__ = 'DEPLOYMENT'

    @property
    def __acl__(self):
        return [
            (Allow, Manager, permissions.view_deployment),
            (Allow, Manager, permissions.add_component)
        ]

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
            multicomponent[name].__parent__ = multicomponent
        else:
            self[name] = new_component
            self[name].__parent__ = self
        return new_component

    def get_component(self, component_type, name=None):
        for component_name, component in self.items():
            matches_component = component_type == component.__class__.name
            matches_name = True if name is None else component_name == name
            if matches_component and matches_name:
                return component
            else:
                subcomponent = component.get_component(component_type, name=name)
                if subcomponent is not None:
                    return subcomponent

    def as_dict(self):
        return {
            'name': self.name,
            'title': self.title,
            'components': {component_name: component.as_dict() for component_name, component in self.items()}
        }
