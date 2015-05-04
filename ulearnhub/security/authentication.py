# -*- coding: utf-8 -*-
from zope.interface import implementer

from max.exceptions import Unauthorized

from ulearnhub.resources import root_factory

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authentication import AuthTktCookieHelper
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.security import Authenticated
from pyramid.security import Everyone

from ulearnhub.models.domains import Domain
# from beaker.cache import cache_region
from webob.cookies import CookieProfile

import requests


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


class CookieGenerator(object):
    def get_cookie_name(self, request):
        calculated_cookie_name = self.__cookie_name__

        if isinstance(request.context, Domain):
            domain_name = request.context.name
        else:
            domain_name = request.params.get('domain')

        calculated_cookie_name = '{}_{}'.format(
            domain_name,
            self.__cookie_name__
        )

        return calculated_cookie_name


class MultiDomainCookieProfile(CookieProfile, CookieGenerator):
    def __init__(self, *args, **kwargs):
        self.__cookie_name__ = ''
        super(MultiDomainCookieProfile, self).__init__(*args, **kwargs)

    @property
    def cookie_name(self):
        return self.__cookie_name__

    @cookie_name.setter
    def cookie_name(self, value):
        self.__cookie_name__ = value

    def bind(self, request):
        """ Bind a request to a copy of this instance and return it"""

        selfish = CookieProfile(
            self.get_cookie_name(request),
            self.secure,
            self.max_age,
            self.httponly,
            self.path,
            self.domains,
            self.serializer,
        )
        selfish.request = request
        return selfish


class MultiDomainAuthTktCookieHelper(AuthTktCookieHelper, CookieGenerator):
    """
    """

    def __init__(self, secret, cookie_name='auth_tkt', secure=False,
                 include_ip=False, timeout=None, reissue_time=None,
                 max_age=None, http_only=False, path="/", wild_domain=True,
                 hashalg='md5', parent_domain=False, domain=None):
        super(MultiDomainAuthTktCookieHelper, self).__init__(
            secret, cookie_name=cookie_name, secure=secure, include_ip=include_ip,
            timeout=timeout, reissue_time=reissue_time, max_age=max_age,
            http_only=http_only, path=path, wild_domain=wild_domain,
            hashalg=hashalg, parent_domain=parent_domain, domain=domain)
        self.__cookie_name__ = self.cookie_name
        self.cookie_profile = MultiDomainCookieProfile(cookie_name, secure, max_age, http_only, path, self.cookie_profile.serializer)

    def identify(self, request):
        self.cookie_name = self.get_cookie_name(request)
        return super(MultiDomainAuthTktCookieHelper, self).identify(request)

    def remember(self, request, userid, max_age=None, tokens=()):
        self.cookie_name = self.get_cookie_name(request)
        return super(MultiDomainAuthTktCookieHelper, self).remember(request, userid, max_age, tokens)

    def forget(self, request):
        self.cookie_name = self.get_cookie_name(request)
        return super(MultiDomainAuthTktCookieHelper, self).forget(request)


class MultiDomainAuthTktAuthenticationPolicy(AuthTktAuthenticationPolicy):
    """
    """
    def __init__(self, *args, **kwargs):
        super(MultiDomainAuthTktAuthenticationPolicy, self).__init__(*args, **kwargs)
        self.cookie = MultiDomainAuthTktCookieHelper(*args, **kwargs)
