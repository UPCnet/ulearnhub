from pyramid.view import view_config

from ulearnhub.views.templates import TemplateAPI


@view_config(route_name='home', renderer='ulearnhub:templates/domains.pt', permission='homepage')
@view_config(route_name='domains', renderer='ulearnhub:templates/domains.pt', permission='homepage')
def domains_view(context, request):
    return {
        "api": TemplateAPI(context, request, 'Domains list')
    }


@view_config(route_name='domain', renderer='ulearnhub:templates/domain.pt')
def domain_view(context, request):
    return {
        "api": TemplateAPI(context, request, 'Domain configuration'),
    }
