test_domain = {
    "name": "test",
    "server": "http://localhost:8081"
}

batch_subscribe_request = {
    "component": {
        "type": "communities",
        "id": "http://localhost/communities"
    },
    "permission_mapping": {
        "mindundi": ['read'],
        "reader": ['read', 'unsubscribe'],
        "writer": ['read', 'write', 'unsubscribe'],
        "owner": ['read', 'write', 'unsubscribe', 'flag']
    },
    "ignore_grants_and_vetos": True,
    "context": "http://localhost/communities/testcommunity",
    "acl": {
        "groups": [
            {"id": "TestGroup", "role": "reader"},
            {"id": "TestGroup2", "role": "writer"},
            {"id": "TestGroup3", "role": "mindundi"},
        ],
        "users": [
            {"id": "testuser1", "role": "writer"},
            {"id": "testowner", "role": "owner"},
            {"id": "testuser.creator", "role": "owner"},
        ]
    }
}

batch_subscribe_request2 = {
    "component": {
        "type": "communities",
        "id": "http://localhost/communities"
    },
    "permission_mapping": {
        "mindundi": ['read'],
        "reader": ['read', 'unsubscribe'],
        "writer": ['read', 'write', 'unsubscribe'],
        "owner": ['read', 'write', 'unsubscribe', 'flag']
    },
    "ignore_grants_and_vetos": True,
    "context": "http://localhost/communities/testcommunity",
    "acl": {
        "groups": [
            {"id": "TestGroup", "role": "reader"},
            {"id": "TestGroup2", "role": "writer"},
        ],
        "users": [
            {"id": "testuser1", "role": "writer"},
            {"id": "testuser.creator", "role": "writer"},
        ]
    }
}

batch_subscribe_request3 = {
    "component": {
        "type": "communities",
        "id": "http://localhost/communities"
    },
    "permission_mapping": {
        "mindundi": ['read'],
        "reader": ['read', 'unsubscribe'],
        "writer": ['read', 'write', 'unsubscribe'],
        "owner": ['read', 'write', 'unsubscribe', 'flag']
    },
    "ignore_grants_and_vetos": True,
    "context": "http://localhost/communities/testcommunity",
    "acl": {
        "groups": [
            {"id": "TestGroup4", "role": "owner"},
        ],
        "users": [
            {"id": "testuser.creator", "role": "owner"},
        ]
    }
}

batch_subscribe_request4 = {
    "component": {
        "type": "communities",
        "id": "http://localhost/communities"
    },
    "permission_mapping": {
        "mindundi": ['read'],
        "reader": ['read', 'unsubscribe'],
        "writer": ['read', 'write', 'unsubscribe'],
        "owner": ['read', 'write', 'unsubscribe', 'flag']
    },
    "ignore_grants_and_vetos": True,
    "context": "http://localhost/communities/testcommunity",
    "acl": {
        "users": [
            {"id": "testuser.creator", "role": "reader"},
            {"id": "testuser.creator", "role": "writer"},
            {"id": "testuser.creator", "role": "owner"},
        ]
    }
}

context = {
    "displayName": "Test",
    "hash": "e6847aed3105e85ae603c56eb2790ce85e212997",
    "url": "http://localhost/communities/testcommunity",
    "permissions": {
        "write": "restricted",
        "subscribe": "restricted",
        "unsubscribe": "subscribed",
        "read": "subscribed",
        "delete": "restricted"
    },
    "objectType": "context"
}

initial_subscriptions = [
    {
        "username": "testuser.creator",
        "permissions": [
            "write",
            "read",
            "unsubscribe"
        ],
    }
]

existing_subscriptions = [
    {
        "username": "testuser.creator",
        "permissions": ["write", "read", "unsubscribe", "flag"],
    }, {
        "username": "groupuser1",
        "permissions": ["write", "read", "unsubscribe"],
    }, {
        "username": "groupuser2",
        "permissions": ["write", "read", "unsubscribe"],
    }, {
        "username": "groupuser3",
        "permissions": ["write", "read", "unsubscribe"],
    }, {
        "username": "groupuser4",
        "permissions": ["write", "read", "unsubscribe"],
    }, {
        "username": "groupuser5",
        "permissions": ["write", "read", "unsubscribe"],
    }, {
        "username": "groupuser6",
        "permissions": ["write", "read", "unsubscribe"],
    }, {
        "username": "testuser1",
        "permissions": ["write", "read", "unsubscribe"],
    }, {
        "username": "testowner",
        "permissions": ["write", "read", "unsubscribe"],
    },

]
ldap_test_group = [
    'groupuser1',
    'groupuser2',
]

ldap_test_group2 = [
    'groupuser3',
    'groupuser4',
]

ldap_test_group3 = [
    'groupuser5',
    'groupuser6',
]

ldap_test_group4 = [
    'groupuser1',
    'testuser.creator',
]
