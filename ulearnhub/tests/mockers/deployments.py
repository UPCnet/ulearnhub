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
        "name": "Test LDAP",
        "port": 636,
        "base_dn": "dc=test,dc=com",
        "admin_cn": "admin",
        "admin_password": "dummy",
        "branch_admin_cn": "branch_admin",
        "branch_admin_password": "dummy",
        "branch_users_dn": "ou=Users",
        "branch_groups_dn": "ou=Groups"
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
