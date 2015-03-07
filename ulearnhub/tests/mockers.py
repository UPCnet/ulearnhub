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
            {"id": "UPCnet.Plone.Admins", "role": "reader"},
        ],
        "users": [
            {"id": "carles.bruguera", "role": "writer"},
        ]
    }
}


context = {
    "displayName": "Test",
    "url": "http://localhost/communities/testcommunity",
    "permissions": {
        "write": "restricted",
        "subscribe": "restricted",
        "unsubscribe": "public",
        "read": "subscribed"
    },
    "objectType": "context"
}

initial_subscriptions = [
    {
        "id": "545cebb1dd0d938859359e38",
        "username": "carles.bruguera",
        "permissions": [
            "read",
            "unsubscribe"
        ],
        "vetos": [
            "write"
        ],
        "grants": [],
    }
]

