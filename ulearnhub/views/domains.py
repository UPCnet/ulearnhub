from pyramid.view import view_config

from ulearnhub.views.templates import TemplateAPI


def get_domain_sections(api):
    sections = [
        dict(url='', title='Information'),
        dict(url='users', title='Users'),
        dict(url='contexts', title='Contexts'),
        dict(url='components', title='Components')
    ]
    for section in sections:
        section['url'] = '{}/domains/{}/{}'.format(api.application_url, api.domain.name, section['url'])
        section['url'] = section['url'].rstrip('/')
        section['active'] = 'active' if api.request.url == section['url'] else ''

    return sections


# @view_config(route_name='domains', renderer='ulearnhub:templates/domains.pt', permission='homepage')
# def domains_view(context, request):
#     return {
#         "api": TemplateAPI(context, request, 'Domains list')
#     }


# @view_config(route_name='domain', renderer='ulearnhub:templates/domain.pt', permission='homepage')
# def domain_view(context, request):
#     api = TemplateAPI(context, request, 'Domain configuration')
#     return {
#         "api": api,
#         "sections": get_domain_sections(api)
#     }


# @view_config(route_name='domain_users', renderer='ulearnhub:templates/users.pt', permission='homepage')
# def domain_users_view(context, request):
#     api = TemplateAPI(context, request, 'Domain users management')
#     return {
#         "api": api,
#         "sections": get_domain_sections(api)
#     }

# @view_config(route_name='domain_user', renderer='ulearnhub:templates/user.pt', permission='homepage')
# def domain_user_view(context, request):
#     api = TemplateAPI(context, request, 'Domain user profile')
#     return {
#         "api": api,
#         "sections": get_domain_sections(api),
#         "username": request.matchdict['username']
#     }


# @view_config(route_name='domain_contexts', renderer='ulearnhub:templates/contexts.pt', permission='homepage')
# def domain_contexts_view(context, request):
#     api = TemplateAPI(context, request, 'Domain contexts management')
#     return {
#         "api": api,
#         "sections": get_domain_sections(api)
#     }


# @view_config(route_name='domain_components', renderer='ulearnhub:templates/components.pt', permission='homepage')
# def domain_components_view(context, request):
#     api = TemplateAPI(context, request, 'Domain contexts management')
#     return {
#         "api": api,
#         "sections": get_domain_sections(api)
#     }
