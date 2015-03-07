from pyramid.response import Response
from pyramid.view import view_config

from ulearnhub.models.domains import Domain
from ulearnhub.models.domains import Domains

from ulearnhub.models.deployments import Deployments
from ulearnhub.models.deployments import Deployment

from ulearnhub.models.components import MaxCluster
from ulearnhub.models.components import MaxServer
from ulearnhub.models.components import LdapServer


@view_config(route_name='initialize')
def initialize(root, request):

    deployments = Deployments()
    root['deployments'] = deployments

    deployment = Deployment(
        name='test',
        title='Test Deployment'
    )
    deployments['test'] = deployment

    ldap_config = {

    }

    maxcluster = MaxCluster('Test Max Cluster')
    maxserver = MaxServer(
        'Test Max Server',
        url='http://localhost:8081')
    ldapserver = LdapServer('LDAP UPC', readonly=True, config=ldap_config)

    maxcluster.components.append(maxserver)

    deployment.components.append(maxcluster)
    deployment.components.append(ldapserver)

    domains = Domains()
    root['domains'] = domains

    test_domain = Domain(
        name='test',
        title='Test Domain',
    )

    test_domain.components.append(ldapserver)
    test_domain.components.append(maxserver)

    domains['test'] = test_domain

    return Response('Initialized')

