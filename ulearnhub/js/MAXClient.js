'use strict';

/**
 * @ngdoc function
 * @name maxClient
 * @description
 * # Factories for accessing to a MAXServer.
 */


var maxClient = angular.module('maxClient', ['ngResource']);

maxClient.factory('Context', ['$resource', 'MAXInfo', function($resource, MAXInfo) {
    return $resource(MAXInfo.max_server+'/contexts:id', null, {
        search: {method:'GET', params: {tags:'@tags', hash:'@hash'}, headers:MAXInfo.headers, isArray: true}
    });
}]);

maxClient.factory('User', ['$resource', 'MAXInfo', function($resource, MAXInfo) {
    return $resource('http://localhost:8081/people/:id', null, {
        query: {method:'GET', isArray: true, headers:MAXInfo.headers},
        save:  {method:'POST', headers:MAXInfo.headers}
    });
}]);

maxClient.factory('UserRoles', ['$resource', 'MAXInfo', function($resource, MAXInfo) {
    return $resource('http://localhost:8081/admin/security/users', null, {
        query: {method:'GET', isArray: true, headers:MAXInfo.headers},
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
    max_server: ''
});

maxClient.factory('_MAXUI', [function() {
    if (window._MAXUI !== undefined) {
        return window._MAXUI;
    } else {
        return false;
    }
}]);

maxClient.directive('oauthinfo', [function() {
    return {
        restrict: 'E',
        controller: function($scope, $element, $attrs, MAXSession) {
            MAXSession.username = $attrs.username;
            MAXSession.oauth_token = $attrs.oauthtoken;
            MAXSession.max_server = $attrs.maxserver;
        }
    };
}]);
