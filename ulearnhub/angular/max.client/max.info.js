(function() {
    'use strict';

/**
 * @ngdoc function
 * @name maxClient dependencies
 * @description
 * # Factories, values and directives used by the MAXClientService.
 */

    angular
        .module('max.client')
        .directive('ngMaxInfo', ngMAXInfo)
        .factory('MAXInfo', MAXInfo)
        .factory('_MAXUI', MAXUI)
        .value('MAXSession', {
            username: '',
            oauth_token: '',
            max_server: '',
            scope: 'widgetcli'
        });

    /**
     * @desc
     */
    /* @nInject */
    function ngMAXInfo() {
        return {
            restrict: 'E',
            controller: function($scope, $element, $attrs, MAXSession) {
                MAXSession.username = $attrs.username;
                MAXSession.oauth_token = $attrs.oauthtoken;
                MAXSession.max_server = $attrs.maxserver;
            }
        };
    }

    /**
     * @desc
     */
    /* @nInject */
    function MAXInfo(MAXSession, _MAXUI) {
        var maxinfo = {};
        if (_MAXUI) {
            maxinfo.headers = {
                'X-Oauth-Username': _MAXUI.username,
                'X-Oauth-Token': _MAXUI.oauth_token,
                'X-Oauth-Scope': 'widgetcli'
            };
            maxinfo.max_server = _MAXUI.max_server;
        } else {
            maxinfo.headers = {
                'X-Oauth-Username': MAXSession.username,
                'X-Oauth-Token': MAXSession.oauth_token,
                'X-Oauth-Scope': 'widgetcli'
            };
            maxinfo.max_server = MAXSession.max_server;
        }
        return maxinfo;
    }

    /**
     * @desc
     */
    /* @nInject */
    function MAXUI() {
        if (window._MAXUI !== undefined) {
            return window._MAXUI;
        } else {
            return false;
        }
    }


})();
