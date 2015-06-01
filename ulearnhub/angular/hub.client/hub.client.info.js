(function() {
    'use strict';

    angular
        .module('hub.client')
        .directive('ngHubInfo', ngHubInfo)
        .factory('hubInfo', hubInfo)
        .value('hubSession', {
            username: '',
            token: '',
            server: ''
        });

    function hubInfo(hubSession) {
        var hubinfo = {};
        hubinfo.headers = {
            'X-Oauth-Username': hubSession.username,
            'X-Oauth-Token': hubSession.token,
            'X-Oauth-Domain': hubSession.domain,
            'X-Oauth-Scope': 'widgetcli'
        };
        hubinfo.server = hubSession.server;
        return hubinfo;
    }


    function ngHubInfo() {
        return {
            restrict: 'E',
            controller: function($scope, $element, $attrs, hubSession) {
                hubSession.username = $attrs.username;
                hubSession.token = $attrs.token;
                hubSession.server = $attrs.server;
                hubSession.domain = $attrs.domain;
            }
        };
    }

})();
