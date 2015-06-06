(function() {
    'use strict';

    angular
        .module('hub')
        .config(config);

    function config(sidebarSectionsProvider, uiSelectConfig, $urlRouterProvider, $translateProvider, $stateProvider) {
        sidebarSectionsProvider.setSections([{
            title: 'Dashboard',
            sref: 'domain',
            icon: 'tachometer'
        }, {
            title: 'Deployments',
            sref: 'deployments',
            icon: 'server'
        }, {
            title: 'Domains',
            sref: 'domains',
            icon: 'globe'
        }, {
            title: 'Users',
            sref: 'users',
            icon: 'user'
        }]);
        uiSelectConfig.theme = 'bootstrap';
        $urlRouterProvider.otherwise('/');

        $translateProvider.useStaticFilesLoader({
            prefix: 'locales/locale-',
            suffix: '.json'
        });

        $translateProvider.preferredLanguage('ca');


        $stateProvider

        .state('domain', {
            url: '',
            templateUrl: 'templates/hub.html',
            resolve: {}
        })

        .state('deployments', {
            url: '/deployments',
            templateUrl: 'templates/deployments.html',
            controller: 'DeploymentListController as deploymentsCtrl',
            resolve: {}
        })

        .state('domains', {
            url: '/domains',
            templateUrl: 'templates/domains.html',
            controller: 'DomainListController as domainsCtrl',
            resolve: {}
        })

        .state('users', {
            url: '/users',
            templateUrl: 'templates/hubusers.html',
            controller: 'HubUsersController as usersCtrl',
            resolve: {}
        });


    }
})();
