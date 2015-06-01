(function() {
    'use strict';

    angular
        .module('hub.domain')
        .config(config);

    /**
     * @desc
     */
    /* @nInject */
    function config(sidebarSectionsProvider, $stateProvider, $urlRouterProvider, $translateProvider, uiSelectConfig) {
        sidebarSectionsProvider.setSections([{
            title: 'Dashboard',
            sref: 'domain',
            icon: 'tachometer'
        }, {
            title: 'Users',
            sref: 'users',
            icon: 'user'
        }, {
            title: 'Contexts',
            sref: 'contexts',
            icon: 'map-marker'
        }, {
            title: 'Api',
            sref: 'api',
            icon: 'paperclip'
        }, {
            title: 'Exceptions',
            sref: 'exceptions',
            icon: 'exclamation-triangle'
        }]);

        uiSelectConfig.theme = 'bootstrap';

        $translateProvider.useStaticFilesLoader({
            prefix: 'locales/locale-',
            suffix: '.json'
        });

        $urlRouterProvider.otherwise('/');
        $translateProvider.preferredLanguage('ca');

        // Route definitions
        $stateProvider
            .state('domain', {
            url: '/',
            templateUrl: 'templates/domain.html',
            resolve: {}
        })

        .state('users', {
            url: '/users',
            templateUrl: 'templates/users.html',
            controller: 'UserListController as usersCtrl',
            resolve: {}
        })

        .state('users.roles', {
            url: '/roles',
            templateUrl: 'templates/users.roles.html',
            controller: 'UsersRolesController as userRol',
            resolve: {}
        })

        .state('contexts', {
            url: '/contexts',
            templateUrl: 'templates/contexts.html',
            controller: 'ContextListController as contextsCtrl',
            resolve: {}
        })

        .state('user', {
            url: '/users/:id',
            templateUrl: 'templates/user.html',
            controller: 'UserProfileController as userCtrl',
            resolve: {}
        })

        .state('context', {
            url: '/contexts/:id',
            templateUrl: 'templates/context.html',
            controller: 'ContextDetailsController as contextCtrl',
            resolve: {}
        })

        .state('api', {
            url: '/api',
            templateUrl: 'templates/api.html',
            controller: 'ApiController as apiCtrl',
            resolve: {
                endpoints: function(EndpointsService) {
                    return EndpointsService.loadEndpoints();
                }
            }
        })

        // This state actually acts as a redirection to the first
        // available method of the endpoint, using api.method state
        .state('api.endpoint', {
            url: '/:endpoint',
            templateUrl: 'templates/api.method.html',
            controller: 'EndpointController as endpointCtrl',
            resolve: {
                expanded: function($stateParams, sidebarSections, endpoints, EndpointsService) {
                    var current_category = EndpointsService.getEndpoint($stateParams.endpoint).category;
                    sidebarSections.expand('api', 'section', true);
                    sidebarSections.expand('api.' + current_category, 'subsection', true);
                    return;
                }
            }

        })

        .state('api.method', {
                url: '/:endpoint/:method',
                templateUrl: 'templates/api.method.html',
                controller: 'EndpointController as endpointCtrl',
                resolve: {
                    expanded: function($stateParams, sidebarSections, endpoints, EndpointsService) {
                        var current_category = EndpointsService.getEndpoint($stateParams.endpoint).category;
                        sidebarSections.expand('api', 'section', true);
                        sidebarSections.expand('api.' + current_category, 'subsection', true);
                        return;
                    }
                }

            })
            .state('exceptions', {
                url: '/exceptions',
                templateUrl: 'templates/exceptions.html',
                controller: 'ExceptionsController as excsCtrl',
                resolve: {}
            })

        .state('exception', {
            url: '/exceptions/:id',
            templateUrl: 'templates/exception.html',
            controller: 'ExceptionController as excCtrl',
            resolve: {}
        });
    }
})();
