from pyramid.view import view_config
from ulearnhub.views.templates import TemplateAPI
from pyramid.view import notfound_view_config
from pyramid.response import Response
from pyramid.renderers import render
from ulearnhub.resources import Domains


@view_config(route_name='domain', renderer='ulearnhub:templates/domain.pt', permission="homepage")
def domain_view(context, request):
    return {
        "api": TemplateAPI(context, request, 'Root')
    }


@view_config(route_name='root', renderer='ulearnhub:templates/root.pt', permission="homepage")
def root_view(context, request):
    return {
        "api": TemplateAPI(context, request, 'Root')
    }


@notfound_view_config(route_name='domain')
def notfound_domain(request):
    template = 'ulearnhub:templates/404.pt'
    return Response(
        render(
            template,
            {
                "error_message": "We couldn't find a domain named {}".format(request.matchdict['domain']),
                "api": TemplateAPI(request.context, request, 'Root')
            },
            request=request
        ), status_code=404
    )


@notfound_view_config()
def notfound_generic(request):
    template = 'ulearnhub:templates/404.pt'
    return Response(
        render(
            template,
            {
                "error_message": "We couldn't find it...",
                "api": TemplateAPI(request.context, request, 'Root')
            },
            request=request
        ), status_code=404
    )
