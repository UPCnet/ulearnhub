from pyramid.view import view_config


@view_config(route_name='domains', request_method='GET', renderer="json")
def domains_list(context, request):
    return [
        dict(name='test', server='http://localhost:8081', oauth_server='https://oauth.upcnet.es'),
        dict(name='test', server='http://localhost:8081', oauth_server='https://oauth.upcnet.es')
    ]
