from pyramid.response import Response
from pyramid.view import view_config

from ulearnhub.models.domains import Domain
from ulearnhub.models.domains import Domains

from ulearnhub.models.deployments import Deployments
from ulearnhub.models.deployments import Deployment

from ulearnhub.models.components import MaxCluster
from ulearnhub.models.components import MaxServer
from ulearnhub.models.components import LdapServer
from ulearnhub.views.templates import TemplateAPI

@view_config(route_name='initialize')
def initialize(root, request):

    deployments = root['deployments'] = Deployments()
    deployment = deployments['test'] = Deployment(name='test', title='Test Deployment')

    ldap_config = {
        "server": "ldap-pre.upc.edu",
        "name": "ldapUPC",
        "port": 636,
        "base_dn": "dc=upc,dc=edu",
        "admin_cn": "ulearn.consulta",
        "admin_password": "",
        "branch_admin_cn": "ulearn.consulta",
        "branch_admin_password": "",
        "branch_users_dn": "ou=Users",
        "branch_groups_dn": "ou=Groups",
        "base_users": [
            {"username": "upcnet.manteniment", "password": ""},
            {"username": "ulearn.user1", "password": ""},
            {"username": "ulearn.user2", "password": ""},
            {"username": "ulearn.user3", "password": ""}
        ]
    }

    maxcluster = MaxCluster('Test Max Cluster')
    maxserver = MaxServer('Test Max Server', url='http://localhost:8081')
    ldapserver = LdapServer('LDAP UPC', readonly=True, config=ldap_config)

    maxcluster.components.append(maxserver)
    deployment.components.append(maxcluster)
    deployment.components.append(ldapserver)

    domains = root['domains'] = Domains()

    test_domain = domains['test'] = Domain(name='test', title='Test Domain')
    test_domain.components.append(ldapserver)
    test_domain.components.append(maxserver)

    return Response('Initialized')


@view_config(route_name='root', renderer='ulearnhub:templates/root.pt', permission="homepage")
def root_view(context, request):
    return {
        "api": TemplateAPI(context, request, 'Root')
    }
