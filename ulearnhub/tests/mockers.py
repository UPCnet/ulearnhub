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
        "reader": ['read'],
        "writer": ['read', 'write'],
        "owner": ['read', 'write']
    },
    "context": "http://localhost/communities/testcommunity",
    "acl": {
        "groups": [
            {"id": "TestGroup", "role": "reader"},
        ],
        "users": [
            {"id": "testuser1", "role": "writer"},
        ]
    }
}


context = {
    "displayName": "Test",
    "url": "http://localhost/communities/testcommunity",
    "permissions": {
        "write": "subscribed",
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
        "vetos": [],
        "grants": [],
    }
]

ldap_test_group = [
    'testuser2',
    'testuser3',
]
