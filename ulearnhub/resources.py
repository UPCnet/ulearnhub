# -*- coding: utf-8 -*-
from ulearnhub.models.deployments import Deployments
from ulearnhub.models.domains import Domains
from ulearnhub.models.users import Users

from pyramid.request import Request
from pyramid.security import Allow
from pyramid.security import Authenticated
from pyramid_zodbconn import get_connection

from persistent.mapping import PersistentMapping

import transaction


class Root(PersistentMapping):
    """
    """
    name = 'root'
    __name__ = 'ROOT'
    __acl__ = [
        (Allow, Authenticated, 'homepage')
    ]


def get_static_connection(registry):
    zodb_dbs = getattr(registry, '_zodb_databases', None)
    primary_db = zodb_dbs.get('')
    primary_conn = primary_db.open()
    return primary_conn


def bootstrap(zodb_root):
    if 'ulearnhub' not in zodb_root:
        root = Root()
        zodb_root['ulearnhub'] = root
        transaction.commit()

    return zodb_root['ulearnhub']


def root_factory(request_or_registry):
    if isinstance(request_or_registry, Request):
        conn = get_connection(request_or_registry)
    else:
        conn = get_static_connection(request_or_registry)
        request_or_registry._temp_zodb_connection = conn

    root = bootstrap(conn.root())
    return root


def initialize_zodb(request):
    root = root_factory(request)
    root.setdefault('deployments', Deployments())
    root.setdefault('domains', Domains())
    root.setdefault('users', Users())

    root['deployments'].__parent__ = root
    root['domains'].__parent__ = root
    root['users'].__parent__ = root
    transaction.commit()
    return root


def create_defaults(registry, defaults, quiet=False):

    def log(message):
        if not quiet:
            print message

    root = initialize_zodb(registry)

    deployments = root['deployments']
    domains = root['domains']
    users = root['users']

    for name, deploy_data in defaults.get('deployments', {}).items():
        if name in deployments:
            log(' · Getting deployment "{}"'.format(name))
        else:
            log(' + Adding deployment "{}"'.format(name))
        deployment = deployments.add(name=name, title=deploy_data['title'])
        for component_data in deploy_data['components']:
            if deployment.get_component(component_data['type'], name=component_data['name']) is None:
                log('   + Added new "{type}" component named "{name}"'.format(**component_data))
                deployment.add_component(component_data['type'], component_data['name'], component_data['title'], component_data['config'])

    for name, domain_data in defaults.get('domains', {}).items():
        if name in domains:
            log(' · Getting domain "{}"'.format(name))
        else:
            log(' + Adding domain "{}"'.format(name))

        domain = domains.add(name=name, title=domain_data['title'])
        for component_data in domain_data['components']:
            if component_data['name'] not in domain:
                component = deployments[component_data['deployment']].get_component(component_data['type'], name=component_data['name'])
                log('   + Assigned "{type}" component named "{name}"'.format(**component_data))
                domain.assign(component)

    for user_data in defaults.get('users', []):
        username = user_data['username']
        domain = user_data['domain']
        roles = user_data['roles']

        log(' · Setting user roles "{}"'.format(name))

        if domain not in users:
            log('   + Adding user {username} on domain {domain} with roles {roles}'.format(**user_data))
            users.add(username, domain, roles)
        else:
            if username not in users[domain]:
                log('   + Adding user {username} on domain {domain} with roles {roles}'.format(**user_data))
                users.add(username, domain, roles)
            else:
                log('   · Setting roles {roles} for user {username} on domain {domain}'.format(**user_data))
                users[domain][username].set_roles(roles)

    transaction.commit()
    registry._temp_zodb_connection.close()
    del registry._temp_zodb_connection
