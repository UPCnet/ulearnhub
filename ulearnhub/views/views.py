from pyramid.view import view_config
from ulearnhub.views.templates import TemplateAPI


@view_config(route_name='root', renderer='ulearnhub:templates/root.pt', permission="homepage")
def root_view(context, request):
    return {
        "api": TemplateAPI(context, request, 'Root')
    }
