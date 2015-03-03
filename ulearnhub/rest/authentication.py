from ulearnhub.rest.exceptions import Unauthorized
from beaker.cache import cache_region
import requests


#@cache_region('oauth_token')
def checkToken(url, username, token, scope):
    payload = {"access_token": token, "username": username}
    payload['scope'] = scope if scope else 'widgetcli'
    return requests.post(url, data=payload, verify=False).status_code == 200


def authenticate(request, allowed_scopes, server='https://oauth.upcnet.es'):
    """
        Autenticates request based on headers.

        Request must provide valid oauth headers, which will be extracted and validated. If
        validation is not successful or there's missing data in the request, an exception
        will be raised. On successful validation, will silently end.
    """

    token = request.headers.get('X-Oauth-Token', '')
    username = request.headers.get('X-Oauth-Username', '')
    scope = request.headers.get('X-Oauth-Scope', '')

    if not token or not username:

        # This is for mental sanity in case we miss the body part when writing tests
        if 'X-Oauth-Username' in request.params.keys():
            raise Unauthorized("Authorization found in url params, not in request. Check your tests, you may be passing the authentication headers as the request body...")

        raise Unauthorized('No auth headers found.')

    if scope not in allowed_scopes:
        raise Unauthorized('The specified scope is not allowed for this resource.')

    valid = checkToken('{}/checktoken'.format(server), username, token, scope)

    if valid:
        def getCreator(request):
            return username

        def getRoles(request):
            security = request.registry.max_security
            user_roles = [role for role, users in security.get("roles", {}).items() if username in users]
            return user_roles + ['Authenticated']

        request.set_property(getCreator, name='creator', reify=True)
        request.set_property(getRoles, name='roles', reify=True)
    else:
        raise Unauthorized('Invalid token.')
