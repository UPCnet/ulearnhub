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
