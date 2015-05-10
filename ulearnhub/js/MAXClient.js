'use strict';

/**
 * @ngdoc function
 * @name maxClient
 * @description
 * # Factories for accessing to a MAXServer.
 */


var maxClient = angular.module('maxClient', ['ngResource']);

maxClient.factory('Endpoints', ['$resource', 'MAXInfo', function($resource, MAXInfo) {
    return $resource(MAXInfo.max_server+'/info/api?by_category=1', null, {
        query: {method:'GET', isArray: true, headers:MAXInfo.headers},
    });
}]);

maxClient.factory('Context', ['$resource', 'MAXInfo', function($resource, MAXInfo) {
    return $resource(MAXInfo.max_server+'/contexts/:id', null, {
        query: {method:'GET', headers:MAXInfo.headers, isArray: true},
        save:  {method:'POST', headers:MAXInfo.headers},
        get:  {method:'GET', headers:MAXInfo.headers},
        remove: {method:'DELETE',headers:MAXInfo.headers},
        update: {method:'PUT',headers:MAXInfo.headers}
    });
}]);

maxClient.factory('ContextAll', ['$resource', 'MAXInfo', function($resource, MAXInfo) {
    return $resource(MAXInfo.max_server+'/contexts?limit=0', null, {
        query: {method:'GET', isArray: true, headers:MAXInfo.headers},
    });
}]);

maxClient.factory('ContextUsers', ['$resource', 'MAXInfo', function($resource, MAXInfo) {
    return $resource(MAXInfo.max_server+'/contexts/:hash/subscriptions', {hash:'@hash'}, {
        query: {method:'GET', headers:MAXInfo.headers, isArray: true},
    });
}]);


maxClient.factory('User', ['$resource', 'MAXInfo', function($resource, MAXInfo) {
    return $resource(MAXInfo.max_server+'/people/:id', null, {
        query: {method:'GET', isArray: true, headers:MAXInfo.headers},
        getUsu:{method:'GET', headers:MAXInfo.headers},
        save:  {method:'POST', headers:MAXInfo.headers},
        remove: {method:'DELETE',headers:MAXInfo.headers},
        update: {method:'PUT',headers:MAXInfo.headers}
    });
}]);

maxClient.factory('UserAll', ['$resource', 'MAXInfo', function($resource, MAXInfo) {
    return $resource(MAXInfo.max_server+'/people?limit=0', null, {
        query: {method:'GET', isArray: true, headers:MAXInfo.headers},
    });
}]);


maxClient.factory('UserFiltered', ['$resource', 'MAXInfo', function($resource, MAXInfo) {
    return $resource(MAXInfo.max_server+'/people?username=:username', {username:'username'}, {
        query: {method:'GET', isArray: true, headers:MAXInfo.headers},
    });
}]);


maxClient.factory('Subscriptions', ['$resource', 'MAXInfo', function($resource, MAXInfo) {
    return $resource(MAXInfo.max_server+'/people/:id/subscriptions', {id:'@id'}, {
        save: {method:'POST', headers:MAXInfo.headers},
    });
}]);

maxClient.factory('UserSubscribe', ['$resource', 'MAXInfo', function($resource, MAXInfo) {
    return $resource(MAXInfo.max_server+'/people/:id/subscriptions/:hash', {id:'@id',hash:'@hash'}, {
        remove: {method:'DELETE', headers:MAXInfo.headers},
    });
}]);

maxClient.factory('UsersRoles', ['$resource', 'MAXInfo', function($resource, MAXInfo) {
    return $resource(MAXInfo.max_server+'/admin/security/users?limit=0', null, {
        query: {method:'GET', isArray: true, headers:MAXInfo.headers},
    });
}]);

maxClient.factory('UserRoleManage', ['$resource', 'MAXInfo', function($resource, MAXInfo) {
    return $resource(MAXInfo.max_server+'/admin/security/roles/:idrol/users/:iduser',
        {idrol:'@idrol', iduser:'@iduser'},{
        save:  {method:'POST', isArray: true, headers:MAXInfo.headers},
        remove: {method:'DELETE',headers:MAXInfo.headers}
    });
}]);

maxClient.factory('UserSubscribeManage', ['$resource', 'MAXInfo', function($resource, MAXInfo) {
    return $resource(MAXInfo.max_server+'/contexts/:hash/permissions/:iduser/:permission',
        {hash:'@hash', iduser:'@iduser',permission:'@permission'},{
        update: {method:'PUT' ,headers:MAXInfo.headers},
        remove: {method:'DELETE',headers:MAXInfo.headers}
    });
}]);

maxClient.factory('ApiInfo', ['$resource', 'MAXInfo', function($resource, MAXInfo) {
    return $resource(MAXInfo.max_server+'/info/api', null, {
        query: {method:'GET'},
        by_category: {method:'GET', params: {by_category:'1'}, isArray: true}
    });
}]);

maxClient.factory('MAXInfo', ['MAXSession', '_MAXUI', function(MAXSession, _MAXUI) {
    var maxinfo = {};
    if (_MAXUI) {
        maxinfo.headers = {'X-Oauth-Username': _MAXUI.username,
                           'X-Oauth-Token': _MAXUI.oauth_token,
                           'X-Oauth-Scope': 'widgetcli'};
        maxinfo.max_server = _MAXUI.max_server;
    } else {
        maxinfo.headers = {'X-Oauth-Username': MAXSession.username,
                           'X-Oauth-Token': MAXSession.oauth_token,
                           'X-Oauth-Scope': 'widgetcli'};
        maxinfo.max_server = MAXSession.max_server;
    }
    return maxinfo;
}]);

maxClient.value('MAXSession', {
    username: '',
    oauth_token: '',
    max_server: '',
    scope: 'widgetcli'
});

maxClient.factory('_MAXUI', [function() {
    if (window._MAXUI !== undefined) {
        return window._MAXUI;
    } else {
        return false;
    }
}]);

maxClient.directive('ngMaxInfo', [function() {
    return {
        restrict: 'E',
        controller: function($scope, $element, $attrs, MAXSession) {
            MAXSession.username = $attrs.username;
            MAXSession.oauth_token = $attrs.oauthtoken;
            MAXSession.max_server = $attrs.maxserver;
        }
    };
}]);
