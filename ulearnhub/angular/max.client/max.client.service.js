(function() {

 /**
 * @ngdoc function
 * @name MAXClientService
 * @description
 * # Service to access MAX Endpoints
 */
    'use strict';

    angular
        .module('max.client')
        .service('MAXClientService', MAXClientService);

    /**
     * @desc
     */
    /* @nInject */
    function MAXClientService($resource, MAXInfo) {

        this.Exception = $resource(
            MAXInfo.max_server+'/admin/maintenance/exceptions/:id',
            null,
            {
                query:  {method:'GET', isArray: true, headers:MAXInfo.headers},
                get:    {method:'GET', headers:MAXInfo.headers}
            }
        );

        this.Context = $resource(
            MAXInfo.max_server+'/contexts/:id',
            null,
            {
                query:  {method:'GET', headers:MAXInfo.headers, isArray: true},
                save:   {method:'POST', headers:MAXInfo.headers},
                get:    {method:'GET', headers:MAXInfo.headers},
                remove: {method:'DELETE',headers:MAXInfo.headers},
                update: {method:'PUT',headers:MAXInfo.headers}
            }
        );

        this.ContextSubscriptions = $resource(
            MAXInfo.max_server+'/contexts/:hash/subscriptions',
            {hash:'@hash'},
            {
                query:  {method:'GET', headers:MAXInfo.headers, isArray: true}
            }
        );

        this.User = $resource(
            MAXInfo.max_server+'/people/:id',
            null,
            {
                query:  {method:'GET', isArray: true, headers:MAXInfo.headers},
                get:    {method:'GET', headers:MAXInfo.headers},
                save:   {method:'POST', headers:MAXInfo.headers},
                remove: {method:'DELETE',headers:MAXInfo.headers},
                update: {method:'PUT',headers:MAXInfo.headers}
            }
        );

        this.UserSubscription = $resource(
            MAXInfo.max_server+'/people/:id/subscriptions/:hash',
            {id:'@id',hash:'@hash'},
            {
                remove: {method:'DELETE', headers:MAXInfo.headers}
            }
        );

        this.UserSubscriptionPermission = $resource(
            MAXInfo.max_server+'/contexts/:hash/permissions/:iduser/:permission',
            {hash:'@hash', iduser:'@iduser',permission:'@permission'},
            {
                update: {method:'PUT' ,headers:MAXInfo.headers},
                remove: {method:'DELETE',headers:MAXInfo.headers}
            }
        );

        this.SecurityUsers = $resource(
            MAXInfo.max_server+'/admin/security/users?limit=0',
            null,
            {
                query:  {method:'GET', isArray: true, headers:MAXInfo.headers}
            }
        );

        this.SecurityUserRole = $resource(
            MAXInfo.max_server+'/admin/security/roles/:idrol/users/:iduser',
            {idrol:'@idrol', iduser:'@iduser'},
            {
                save:   {method:'POST', isArray: true, headers:MAXInfo.headers},
                remove: {method:'DELETE',headers:MAXInfo.headers}
            }
        );

        this.ApiInfo = $resource(
            MAXInfo.max_server+'/info/api',
            null,
            {
                query: {method:'GET'},
                by_category: {method:'GET', params: {by_category:'1'}, isArray: true}
            }
        );
    }
})();
