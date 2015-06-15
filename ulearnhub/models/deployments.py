# -*- coding: utf-8 -*-
from ulearnhub.models.components import get_component
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

    def as_list(self):
        entries = []
        for name, deployment in self.items():
            entries.append(deployment.as_dict())
        return entries


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

    def add_component(self, component_type, name, title, params, parent_component=None):
        Component = get_component(component_type)
        new_component = Component(name, title, params)

        # set who's gonna hold this component: another component or the deployment itself
        parent = parent_component if parent_component is not None else self

        parent[name] = new_component
        parent[name].__parent__ = parent
        return new_component

    def get_component(self, component_type, name=None):
        ComponentClass = get_component(component_type)
        for component_name, component in self.items():
            matches_component = ComponentClass == component.__class__
            matches_name = True if name is None else component_name == name
            if matches_component and matches_name:
                return component
            else:
                subcomponent = component.get_component(ComponentClass, name=name)
                if subcomponent is not None:
                    return subcomponent

    def as_dict(self):
        return {
            'name': self.name,
            'title': self.title,
            'components': [component.as_dict() for component_name, component in self.items()]
        }
