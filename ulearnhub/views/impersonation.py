from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from ulearnhub.views.templates import TemplateAPI
from ulearnhub.views.login import get_max_user_data
from ulearnhub.security import permissions
import requests


def getTokenFor(server, username):
    payload = {
        "grant_type": 'password',
        "scope": 'widgetcli',
        "username": username,
        "password": "itdoesntmatter"
    }
    resp = requests.post('{}/token-bypass'.format(server), data=payload, verify=False)
    token = resp.json().get('access_token')
    return token


@view_config(route_name='domain_impersonate', permission=permissions.impersonate)
def impersonate_view(domain, request):
    api = TemplateAPI(domain, request, "uLearn HUB Impersonate")
    username = request.matchdict.get('username', '')

    if username is not None:
        impersonated_token = getTokenFor(domain.oauth_server, username)
        if impersonated_token:
            request.session[domain.name]['impersonation'] = {}
            request.session[domain.name]['impersonation']['token'] = impersonated_token

            client = domain.maxclient
            client.setActor(username)
            client.setToken(impersonated_token)
            user_data = get_max_user_data(client, username)
            request.session[domain.name]['impersonation'].update(user_data)
        else:
            request.session[domain.name]['error'] = 'Could not impersonate as {}'.format(username)

    return HTTPFound(location='{}/{}'.format(api.application_url, domain.name))


@view_config(route_name='domain_impersonate_exit', permission=permissions.impersonate)
def unimpersonate_view(domain, request):
    api = TemplateAPI(domain, request, "uLearn HUB Impersonation")

    try:
        del request.session[domain.name]['impersonation']
    except:
        print "Cannot cancel impersonation"

    return HTTPFound(location='{}/{}'.format(api.application_url, domain.name))
