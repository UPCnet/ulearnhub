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
    }
})();
