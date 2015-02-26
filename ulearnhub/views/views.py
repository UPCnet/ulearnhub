from pyramid.response import Response
from pyramid.view import view_config

from ulearnhub.views.templates import TemplateAPI


@view_config(route_name='home', renderer='ulearnhub:templates/home.pt', permission='homepage')
def my_view(request):
    page_title = "uLearn HUB Login"
    api = TemplateAPI(request, page_title)
    return {
        "api": api
    }
