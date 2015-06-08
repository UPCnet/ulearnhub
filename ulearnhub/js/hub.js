(function() {
    'use strict';

    angular
        .module('hub', [
            'datatables',
            'datatables.bootstrap',
            'ui.bootstrap',
            'ui.router',
            'ui.select',
            'ngSanitize',
            'ngCookies',
            'pascalprecht.translate',

            'hub.sidebar',
            'hub.client',
            'hub.translations'
    ]);

})();

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
    config.$inject = ["sidebarSectionsProvider", "uiSelectConfig", "$urlRouterProvider", "$translateProvider", "$stateProvider"];
})();

(function() {
    'use strict';

    angular
        .module('hub')
        .controller('MainAppController', MainAppController);


    /**
     * @desc
     */
    /* @nInject */
    function MainAppController(sidebarSections, $translate) {
        var self = this;
        self.sidebar_status = '';
        self.toggleSidebar = toggleSidebar;
        self.changeLanguage = changeLanguage;

        ///////////////////////////


        function toggleSidebar(){
            var collapsed = sidebarSections.toggle();
            self.sidebar_status = collapsed ? '' : 'page-sidebar-toggled';
        }

        function changeLanguage(key) {
            $translate.use(key);
        }
    }
    MainAppController.$inject = ["sidebarSections", "$translate"];
})();

(function() {
    'use strict';

    angular
        .module('hub')
        .controller('HubUsersController', HubUsersController);

    /**
     * @desc
     */
    /* @nInject */
    function HubUsersController($cookies, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, HUBClientService) {
        var self = this;
        var lang = $cookies.currentLang;
        // Default datatable options
        self.dtOptions = DTOptionsBuilder
            .newOptions().withPaginationType('full_numbers')
            .withBootstrap()
            .withLanguage(DTTranslations[lang]);
        self.dtColumnDefs = [
            DTColumnDefBuilder.newColumnDef(0),
            DTColumnDefBuilder.newColumnDef(1),
            DTColumnDefBuilder.newColumnDef(2)
        ];
        self.users = HUBClientService.User.query();
        self.domains = HUBClientService.Domain.query();
        self.newuser = {};


        self.changeRole = changeRole;
        self.add = add;
        //////////////////////////////

        /**
         * @desc
         */
        function changeRole(user, role) {
            if (role.active === true) {
                HUBClientService.UserRole.update({
                    role: role.role,
                    domain: user.domain,
                    username: user.username
                }, {});
            } else {
                HUBClientService.UserRole.remove({
                    domain: user.domain,
                    role: role.role,
                    username: user.username
                });
            }
        }

        /**
         * @desc
         */

         function add() {

            HUBClientService.User.save(
                {username:self.newuser.username, domain: self.newuser.domain.name},
                function() {
                //success
                },
                function() {
                //fail
            });
         }

    }
    HubUsersController.$inject = ["$cookies", "DTOptionsBuilder", "DTTranslations", "DTColumnDefBuilder", "HUBClientService"];
})();

(function() {
    'use strict';

    angular
        .module('hub')
        .controller('DomainListController', DomainListController)
        .controller('NewDomainModalController', NewDomainModalController);

    /**
     * @desc
     */
    /* @nInject */
    function DomainListController($cookies, $modal, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, HUBClientService) {


        var self = this;
        var lang = $cookies.currentLang;
        // Default datatable options
        self.dtOptions = DTOptionsBuilder
            .newOptions().withPaginationType('full_numbers')
            .withBootstrap()
            .withLanguage(DTTranslations[lang]);

        self.dtColumnDefs = [
            DTColumnDefBuilder.newColumnDef(0),
            DTColumnDefBuilder.newColumnDef(1),
            DTColumnDefBuilder.newColumnDef(2)
        ];

        self.domains = HUBClientService.Domain.query();


        self.openModal = function(size) {

            var modalInstance = $modal.open({
                templateUrl: 'new-domain.html',
                controller: 'ModalInstanceCtrl',
                size: size
            });

            modalInstance.result
                .then(function(newdomain) {
                    self.domains.push(newdomain);
                });
        };
    }
    DomainListController.$inject = ["$cookies", "$modal", "DTOptionsBuilder", "DTTranslations", "DTColumnDefBuilder", "HUBClientService"];


    /**
     * @desc
     */
    /* @nInject */
    function NewDomainModalController($scope, $modalInstance, HUBClientService) {
    $scope.alerts = [];

    $scope.ok = function() {
        HUBClientService.Domain.save($scope.newdomain)
            .$promise.then(function(data) {
                $modalInstance.close(data);
            }, function(error) {
                $scope.alerts.push({
                    type: 'danger',
                    msg: error.data.error + ': ' + error.data.error_description
                });
            });
    };

    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };

    $scope.closeAlert = function(index) {
        $scope.alerts.splice(index, 1);
    };
    }
    NewDomainModalController.$inject = ["$scope", "$modalInstance", "HUBClientService"];

})();

(function() {
    'use strict';

    angular
        .module('hub')
        .controller('DeploymentListController', DeploymentsListController)
        .controller('NewDeploymentModalController', NewDeploymentModalController);

    /**
     * @desc
     */
    /* @nInject */
    function DeploymentsListController($cookies, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, HUBClientService) {
        var self = this;
        var lang = $cookies.currentLang;
        // Default datatable options
        self.dtOptions = DTOptionsBuilder
            .newOptions().withPaginationType('full_numbers')
            .withBootstrap()
            .withLanguage(DTTranslations[lang]);

        self.dtColumnDefs = [
            DTColumnDefBuilder.newColumnDef(0),
            DTColumnDefBuilder.newColumnDef(1),
            DTColumnDefBuilder.newColumnDef(2)
        ];

        self.domains = HUBClientService.Domain.query();


        self.open = function(size) {

            var modalInstance = $modal.open({
                templateUrl: 'new-domain.html',
                controller: 'ModalInstanceCtrl',
                size: size
            });

            modalInstance.result
                .then(function(newdomain) {
                    self.domains.push(newdomain);
                });
        };
    }
    DeploymentsListController.$inject = ["$cookies", "DTOptionsBuilder", "DTTranslations", "DTColumnDefBuilder", "HUBClientService"];

    /**
     * @desc
     */
    /* @nInject */
    function NewDeploymentModalController($scope, $modalInstance, $modal, HUBClientService) {

        $scope.alerts = [];

        $scope.ok = function() {
            HUBClientService.Domain.save($scope.newdomain)
                .$promise.then(function(data) {
                    $modalInstance.close(data);
                }, function(error) {
                    $scope.alerts.push({
                        type: 'danger',
                        msg: error.data.error + ': ' + error.data.error_description
                    });
                });
        };

        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
        };

        $scope.closeAlert = function(index) {
            $scope.alerts.splice(index, 1);
        };
    }
    NewDeploymentModalController.$inject = ["$scope", "$modalInstance", "$modal", "HUBClientService"];

})();

(function() {
    'use strict';

    angular
        .module('hub.client', [
            'ngResource'
    ]);

})();

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
    hubInfo.$inject = ["hubSession"];


    function ngHubInfo() {
        return {
            restrict: 'E',
            controller: ["$scope", "$element", "$attrs", "hubSession", function($scope, $element, $attrs, hubSession) {
                hubSession.username = $attrs.username;
                hubSession.token = $attrs.token;
                hubSession.server = $attrs.server;
                hubSession.domain = $attrs.domain;
            }]
        };
    }

})();

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
    }
    HUBClientService.$inject = ["$resource", "hubInfo"];
})();

(function() {
    'use strict';

    angular
        .module('hub.sidebar', [
            'ui.router'
    ]);

})();

(function() {
    'use strict';

    angular
        .module('hub.sidebar')
        .provider('sidebarSections', sidebarSectionsProvider);

    /**
     * @desc
     */
    /* @nInject */
    function sidebarSectionsProvider() {
        var sections = [];
        var collapsed = true;
        var expands = {
            section: undefined,
            subsection: undefined
        };

        this.$get = SidebarSections;
        this.setSections = setSections;

        ///////////////////////////

        function setSections(value) {
            sections = value;
        }

        function SidebarSections() {

            var service = {
                toggle: toggle,
                get: get,
                add: add,
                subsection: subsection,
                expanded: expanded,
                expand: expand
            };

            return service;

            /////////////////

            /**
             * @desc
             */
            function toggle() {
                collapsed = !collapsed;
                return collapsed;
            }

            /**
             * @desc
             */
            function get() {
                return sections;
            }

            /**
             * @desc
             */
            function add(newsection) {
                sections.push(newsection);
            }

            /**
             * @desc
             */
            function subsection(section_sref, items) {
                var section = sections.filter(function(el) {
                    return el.sref === section_sref;
                })[0];
                sections[sections.indexOf(section)].subsections = items;
                return section;
            }

            /**
             * @desc
             */
            function expanded(section, which) {
                var value = expands[which] === section;
                return value;
            }

            /**
             * @desc
             */
            function expand(section, which, force) {
                if (expands[which] !== section | force === true) {
                    expands[which] = section;
                } else {
                    expands[which] = undefined;
                }
            }

        }
    }
})();

(function() {
    'use strict';

    angular
        .module('hub.sidebar')
        .controller('SidebarController', SidebarController);

    /**
     * @desc
     */
    /* @nInject */
    function SidebarController($state, $stateParams, sidebarSections) {
        var self = this;

        self.sections = sidebarSections.get();
        self.expands = {
            section: undefined,
            subsection: undefined
        };

        self.active = active;
        self.has_sub = has_sub;
        self.expanded = expanded;
        self.expand = expand;

        ////////////////////////

        /**
         * @desc
         */
        function active(section_sref_or_href, sref) {
            var sidebar_url;
            if (sref) {
                sidebar_url = $state.href(section_sref_or_href);
            } else {
                sidebar_url = section_sref_or_href;
            }
            var current_url = $state.href($state.current.name, $stateParams);
            var parent = new RegExp(sidebar_url + '/', "g");
            var is_child = current_url ? current_url.match(parent) !== null : false;
            is_child = is_child && sidebar_url !== '#';
            var is_same = current_url === sidebar_url;
            var is_active = is_child | is_same;
            return is_active ? 'active' : '';
        }

        /**
         * @desc
         */
        function has_sub(subsection) {
            var effective_subsections = subsection === undefined ? [] : subsection;
            return effective_subsections.length > 0 ? 'has-sub' : '';
        }

        /**
         * @desc
         */
        function expanded(section, which) {
            return sidebarSections.expanded(section, which);
        }

        /**
         * @desc
         */
        function expand(section, which) {
            return sidebarSections.expand(section, which);
        }

    }
    SidebarController.$inject = ["$state", "$stateParams", "sidebarSections"];
})();

(function() {
    'use strict';

    angular
        .module('hub.translations', [
    ]);

})();

(function() {
    'use strict';

    angular
        .module('hub.translations')
        .constant('DTTranslations', {
            es: {
                'sProcessing': 'Procesando...',
                'sLengthMenu': 'Mostrar _MENU_ registros',
                'sZeroRecords': 'No se encontraron resultados',
                'sEmptyTable': 'Ningún dato disponible en esta tabla',
                'sInfo': 'Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros',
                'sInfoEmpty': 'Mostrando registros del 0 al 0 de un total de 0 registros',
                'sInfoFiltered': '(filtrado de un total de _MAX_ registros)',
                'sInfoPostFix': '',
                'sSearch': 'Buscar:',
                'sUrl': '',
                'sInfoThousands': '.',
                'sLoadingRecords': 'Cargando...',
                'oPaginate': {
                    'sFirst': 'Primero',
                    'sLast': 'Último',
                    'sNext': 'Siguiente',
                    'sPrevious': 'Anterior'
                },
                'oAria': {
                    'sSortAscending': ': Activar para ordenar la columna de manera ascendente',
                    'sSortDescending': ': Activar para ordenar la columna de manera descendente'
                }
            },
            ca: {
                'sProcessing': 'Processant...',
                'sLengthMenu': 'Mostra _MENU_ registres',
                'sZeroRecords': 'No s\'han trobat registres.',
                'sEmptyTable': 'No hi ha cap dada disponible en aquesta taula',
                'sInfo': 'Mostrant de _START_ a _END_ de _TOTAL_ registres',
                'sInfoEmpty': 'Mostrant de 0 a 0 de 0 registres',
                'sInfoFiltered': '(filtrat de _MAX_ total registres)',
                'sInfoPostFix': '',
                'sSearch': 'Filtrar:',
                'sUrl': '',
                'sInfoThousands': '.',
                'sLoadingRecords': 'Carregant...',
                'oPaginate': {
                    'sFirst': 'Primer',
                    'sPrevious': 'Anterior',
                    'sNext': 'Següent',
                    'sLast': 'Últim'
                },
                'oAria': {
                    'sSortAscending': ': Activa per ordenar la columna de manera ascendente',
                    'sSortDescending': ': Activa per ordenar la columna de manera descendente'
                }
            },
            en: {
                'sEmptyTable': 'No data available in table',
                'sInfo': 'Showing _START_ to _END_ of _TOTAL_ entries',
                'sInfoEmpty': 'Showing 0 to 0 of 0 entries',
                'sInfoFiltered': '(filtered from _MAX_ total entries)',
                'sInfoPostFix': '',
                'sInfoThousands': ',',
                'sLengthMenu': 'Show _MENU_ entries',
                'sLoadingRecords': 'Loading...',
                'sProcessing': 'Processing...',
                'sSearch': 'Search:',
                'sZeroRecords': 'No matching records found',
                'oPaginate': {
                    'sFirst': 'First',
                    'sLast': 'Last',
                    'sNext': 'Next',
                    'sPrevious': 'Previous'
                },
                'oAria': {
                    'sSortAscending': ': activate to sort column ascending',
                    'sSortDescending': ': activate to sort column descending'
                }
            }
        });
})();
