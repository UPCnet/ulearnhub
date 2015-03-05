from pyramid.response import Response
from pyramid.view import view_config

from ulearnhub.models.domains import Domain
from ulearnhub.models.domains import Domains

from ulearnhub.views.templates import TemplateAPI


@view_config(route_name='initialize')
def initialize(root, request):
    domains = Domains()
    domains = root['domains'] = domains

    test_domain = Domain(
        name='test',
        server='http://localhost:8081',
    )

    domains['test'] = test_domain

    return Response('Initialized')


@view_config(route_name='root', renderer='ulearnhub:templates/root.pt', permission="homepage")
def root_view(context, request):
    return {
        "api": TemplateAPI(context, request, 'Root')
    }
