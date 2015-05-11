# -*- coding: utf-8 -*-
"""
    Definitions of routes used on the api endpoints.

    This routes are loaded on application initialization, and its parameters
    used to configure the route as it's added.

    The routes have one required paramter "route" that defines the URI that will
    be used by pyramid router to match views with.

    There is a "traverse" parameter that if present, will be used to tell pyramid
    which object should try to traverse to be the context of a request. URI's used in
    this parameter don't have to match URI in "route" param, but they must conform to
    existing Traversers on the Root context. see max.resources for more info. Routes
    defined without "traverse", will have the Root context as the request context.

    Finally there are keys used in the api info endpoint to classify the endpoints.
    Routes in this file are sorted by the kind of traverser used. "category"
    parameter defines a classification based on a more 'high level' view of the endpoint.
    For example "subcriptions" resource is classified on "Subscriptions" even if it's
    using the people traverser, in order to group it with all other subscription related endpoints.

    IMPORTANT! Routes with fixed path segments, that must override routes with the same pattern but
    with dynamic segments, must be defined earlier, if not, pyramid router will match the dynamic one first.
    For example, /activities/comments must be defined earlier that /activities/{activityid}.
"""

from collections import OrderedDict

ROUTES = OrderedDict()

# DEPLOYMENT ENDPOINTS
ROUTES['api_deployments'] = dict(route='/api/deployments', traverse='/deployments')
ROUTES['api_deployment'] = dict(route='/api/deployments/{deployment}', traverse='/deployments/{deployment}')
ROUTES['api_deployment_components'] = dict(route='/api/deployments/{deployment}/components', traverse='/deployments/{deployment}')
ROUTES['api_deployment_component'] = dict(route='/api/deployments/{deployment}/components/{component}', traverse='/deployments/{deployment}')

# DOMAIN ENDPOINTS
ROUTES['api_domains'] = dict(route='/api/domains', traverse='/domains')
ROUTES['api_domain'] = dict(route='/api/domains/{domain}', traverse='/domains/{domain}')
ROUTES['api_domain_components'] = dict(route='/api/domains/{domain}/components', traverse='/domains/{domain}')

# USER ENDPOINTS

ROUTES['api_users'] = dict(route='/api/users', traverse='/users')

# SERVICES ENDPOINTS
ROUTES['api_domain_services'] = dict(route='/api/domains/{domain}/services', traverse='/domains/{domain}')
ROUTES['api_domain_service'] = dict(route='/api/domains/{domain}/services/{service}', traverse='/domains/{domain}/services/{service}')

# NON-API ROUTES
ROUTES['root'] = dict(route='/')
ROUTES['login'] = dict(route='/login')
ROUTES['logout'] = dict(route='/logout')
ROUTES['info'] = dict(route='/info', traverse='/domains')

# DOMAIN-RELATED VIEWS
# Those must be declared last to not override root views
ROUTES['domain'] = dict(route='/{domain}', traverse="/domains/{domain}")
ROUTES['domain_login'] = dict(route='/{domain}/login', traverse="/domains/{domain}")
ROUTES['domain_logout'] = dict(route='/{domain}/logout', traverse="/domains/{domain}")
