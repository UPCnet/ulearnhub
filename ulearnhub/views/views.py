from pyramid.response import Response
from pyramid.view import view_config

from ulearnhub.views.templates import TemplateAPI


@view_config(route_name='home', renderer='ulearnhub:templates/domains.pt', permission='homepage')
@view_config(route_name='domains', renderer='ulearnhub:templates/domains.pt', permission='homepage')
def my_view(request):
    page_title = "uLearn HUB Login"
    api = TemplateAPI(request, page_title)
    return {
        "api": api
    }


@view_config(route_name='users', renderer='ulearnhub:templates/users.pt', permission='homepage')
def users_view(request):
    page_title = "uLearn Users Manage"
    api = TemplateAPI(request, page_title)
    return {
        "api": api
    }
