test_deployment = {
    'name': 'test',
    'title': 'Test Deployment'
}

test_ldap_component = {
    'component': 'ldapserver',
    'name': 'testldap',
    'title': 'Test LDAP',
    'params': {
        "server": "testldap",
        "readonly": True,
        "name": "Test LDAP",
        "admin_dn": "admin",
        "admin_password": "dummy",
        "users_base_dn": "ou=Users",
        "user_scope": "SCOPE_SUBTREE",
        "group_base_dn": "ou=Groups",
        "group_scope": "SCOPE_SUBTREE",
        "branches": {
            "enabled": False
        }
    }
}

test_communities_component = {
    'component': 'ulearncommunities',
    'name': 'testcommunities',
    'title': 'Test ULearn Communities',
    'params': {
        "url": "http://test.communities",
        "api_username": "admin",
        "api_password": "dummy",
    }
}
test_maxcluster_component = {
    'component': 'maxcluster',
    'name': 'testmaxcluster',
    'title': 'Test MaxCluster',
    'params': {
        'server': 'localhost',
        'instances_root': '/var/max'
    }
}

test_maxserver_component = {
    'component': 'maxserver',
    'name': 'testmaxserver1',
    'title': 'Test MaxServer',
    'params': {
        'url': 'http://localhost:8081',
    }
}

RABBIT_URL = "amqp://guest:guest@localhost:5672"
TEST_VHOST_URL = '{}/tests'.format(RABBIT_URL)
RABBIT_MANAGEMENT_URL = "http://localhost:15672/api".format(RABBIT_URL)

test_rabbitserver_component = {
    'component': 'rabbitserver',
    'name': 'testrabbit',
    'title': 'Test RabbitServer',
    'params': {
        'url': TEST_VHOST_URL,
    }
}
