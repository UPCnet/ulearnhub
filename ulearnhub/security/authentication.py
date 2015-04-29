# -*- coding: utf-8 -*-
from zope.interface import implementer

from ulearnhub.resources import root_factory
from max.exceptions import Unauthorized

from pyramid.interfaces import IAuthenticationPolicy
from pyramid.security import Authenticated
from pyramid.security import Everyone

from beaker.cache import cache_region

import requests


#@cache_region('oauth_token')
def check_token(url, username, token, scope):
    """
        Checks if a user matches the given token.
    """
    payload = {"access_token": token, "username": username}
    payload['scope'] = scope if scope else 'widgetcli'
    return requests.post('{}/checktoken'.format(url), data=payload, verify=False).status_code == 200


@implementer(IAuthenticationPolicy)
class OauthAuthenticationPolicy(object):
    """
        Pyramid authentication policy against OAuth2 provided on headers
        and principals stored on database.
    """
    def __init__(self, allowed_scopes):
        self.allowed_scopes = allowed_scopes
        self._authenticated_userid = ''
        self._effective_principals = []

    # Helper methods

    def _validate_user(self, request):
        """
            Extracts and validates user from the request.

            Performs several checks that will result on Unauthorized
            exceptions if failed. At the end the successfully authenticated
            username is returned.

        """
        # Discard non-api requests
        if not request.matched_route.name.startswith('api_'):
            return None

        username, oauth_token, scope = request.auth_headers
        domain_name = request.auth_domain
        if domain_name is None:
            raise Unauthorized('Missing domain on authorization headers.')

        if scope not in self.allowed_scopes:
            raise Unauthorized('The specified scope is not allowed for this resource.')

        domain = root_factory(request)['domains'].get(domain_name)
        if domain is None:
            raise Unauthorized('The specified domain is not registered on this hub.')

        valid = check_token(
            domain.oauth_server,
            username, oauth_token, scope,
        )

        if not valid:
            raise Unauthorized('Invalid token.')

        request.__authenticated_userid__ = username
        return username

    def _get_principals(self, request):
        """
            Calculates the identities that can be used
            when authorizing the user
        """
        if request.authenticated_userid is None:
            return []

        principals = [Everyone, Authenticated, request.authenticated_userid]

        current_domain = request.auth_domain or request.session.get('domain', None)
        if current_domain:
            domain_users = root_factory(request)['users'].get(current_domain, {})
            domain_user = domain_users.get(request.authenticated_userid, None)
            if domain_user:
                principals.extend(domain_user.roles)
        else:
            return principals

        request.__effective_principals__ = principals
        return principals

    # IAuthenticationPolicy Implementation

    def authenticated_userid(self, request):
        """
            Returns the oauth2 authenticated user.

            On first acces, user is extracted from Oauth headers and validated. Extracted
            user id is cached to future accesses to the property
        """
        try:
            return request.__authenticated_userid__
        except AttributeError:
            return self._validate_user(request)

    def unauthenticated_userid(self, request):
        """
            DUP of authenticated_userid
        """
        return self.authenticated_userid   # pragma: no cover

    def effective_principals(self, request):
        """
            Returns
        """
        try:
            return request.__effective_principals__
        except AttributeError:
            return self._get_principals(request)

    def remember(self, request, principal, **kw):
        """ Not used neither needed """
        return []  # pragma: no cover

    def forget(self, request):
        """ Not used neither needed"""
        return []  # pragma: no cover
