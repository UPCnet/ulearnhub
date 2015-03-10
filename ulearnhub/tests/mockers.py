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
        "reader": ['read', 'unsubscribe'],
        "writer": ['read', 'write', 'unsubscribe'],
        "owner": ['read', 'write', 'unsubscribe']
    },
    "context": "http://localhost/communities/testcommunity",
    "acl": {
        "groups": [
            {"id": "TestGroup", "role": "reader"},
        ],
        "users": [
            {"id": "testuser1", "role": "writer"},
            {"id": "testuser.creator", "role": "owner"},
        ]
    }
}


context = {
    "displayName": "Test",
    "url": "http://localhost/communities/testcommunity",
    "permissions": {
        "write": "restricted",
        "subscribe": "restricted",
        "unsubscribe": "subscribed",
        "read": "subscribed"
    },
    "objectType": "context"
}

initial_subscriptions = [
    {
        "id": "545cebb1dd0d938859359e38",
        "username": "testuser.creator",
        "permissions": [
            "write",
            "read",
            "unsubscribe"
        ],
        "vetos": [
        ],
        "grants": ['write'],
    }
]

ldap_test_group = [
    'testuser2',
    'testuser3',
]
