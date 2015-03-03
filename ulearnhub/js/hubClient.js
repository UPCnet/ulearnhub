'use strict';

/**
 * @ngdoc function
 * @name hubClient
 * @description
 * # Factories for accessing to a hubServer.
 */


var hubClient = angular.module('hubClient', ['ngResource']);


hubClient.factory('Domain', ['$resource', 'hubInfo', function($resource, hubInfo) {
    return $resource(hubInfo.server + '/api/domains/:id', null, {
        query: {method:'GET', isArray: true, headers:hubInfo.headers}
    });
}]);


hubClient.factory('hubInfo', ['hubSession', function(hubSession) {
    var hubinfo = {};
    hubinfo.headers = {'X-Oauth-Username': hubSession.username,
                       'X-Oauth-Token': hubSession.token,
                       'X-Oauth-Scope': 'widgetcli'};
    hubinfo.server = hubSession.server;
    return hubinfo;
}]);


hubClient.value('hubSession', {
    username: '',
    token: '',
    server: ''
});


hubClient.directive('ngHubInfo', [function() {
    return {
        restrict: 'E',
        controller: function($scope, $element, $attrs, hubSession) {
            hubSession.username = $attrs.username;
            hubSession.token = $attrs.token;
            hubSession.server = $attrs.server;
        }
    };
}]);
