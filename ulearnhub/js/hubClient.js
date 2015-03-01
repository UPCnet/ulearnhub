'use strict';

/**
 * @ngdoc function
 * @name hubClient
 * @description
 * # Factories for accessing to a hubServer.
 */


var hubClient = angular.module('hubClient', ['ngResource']);

hubClient.factory('Domains', ['$resource', 'hubInfo', function($resource, hubInfo) {
    return $resource(hubInfo.max_server+'/domains', null, {
        query: {method:'GET', isArray: true, headers:hubInfo.headers}
    });
}]);

hubClient.factory('hubInfo', ['hubSession', function(hubSession) {
    var maxinfo = {};
    maxinfo.headers = {'X-Oauth-Username': hubSession.username,
                       'X-Oauth-Token': hubSession.oauth_token,
                       'X-Oauth-Scope': 'widgetcli'};
    maxinfo.max_server = hubSession.max_server;
    return maxinfo;
}]);

hubClient.value('hubSession', {
    username: '',
    oauth_token: '',
    max_server: ''
});


hubClient.directive('ngHubInfo', [function() {
    return {
        restrict: 'E',
        controller: function($scope, $element, $attrs, hubSession) {
            hubSession.username = $attrs.username;
            hubSession.oauth_token = $attrs.oauthtoken;
            hubSession.hub_server = $attrs.hubserver;
        }
    };
}]);
