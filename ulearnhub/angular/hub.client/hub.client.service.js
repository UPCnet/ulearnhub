(function() {

 /**
 * @ngdoc function
 * @name HUBClientService
 * @description
 * # Service to access HUB Endpoints
 */
    'use strict';

    angular
        .module('hub.client')
        .service('HUBClientService', HUBClientService);

    /**
     * @desc
     */
    /* @nInject */
    function HUBClientService($resource, hubInfo) {

        this.Domain = $resource(
            hubInfo.server + '/api/domains/:id',
            null,
            {
                query: {method:'GET', isArray: true, headers:hubInfo.headers},
                save: {method:'POST', headers:hubInfo.headers},
                get: {method:'GET', headers:hubInfo.headers}
            }
        );
        this.Deployment = $resource(
            hubInfo.server + '/api/deployments/:name',
            null,
            {
                query: {method:'GET', isArray: true, headers:hubInfo.headers},
                save: {method:'POST', headers:hubInfo.headers},
                get: {method:'GET', headers:hubInfo.headers}
            }
        );
        this.User = $resource(
            hubInfo.server + '/api/users/:username',
            null,
            {
                query: {method:'GET', isArray: true, headers:hubInfo.headers},
                save: {method:'POST', headers:hubInfo.headers}
            }
        );
        this.UserRole = $resource(
            hubInfo.server + '/api/users/:domain/:username/roles/:role',
            null,
            {
                remove: {method:'DELETE', headers:hubInfo.headers},
                update: {method:'PUT', headers:hubInfo.headers}
            }
        );
        this.Exception = $resource(
            hubInfo.server+'/api/exceptions/:hash',
            null,
            {
                query:  {method:'GET', isArray: true, headers:hubInfo.headers},
                get:    {method:'GET', headers:hubInfo.headers},
                remove: {method:'DELETE', headers:hubInfo.headers}
            }
        );

    }
})();
