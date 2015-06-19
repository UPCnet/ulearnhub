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
            'formly',
            'formlyBootstrap',

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

    function config(sidebarSectionsProvider, uiSelectConfig, $urlRouterProvider, $translateProvider, $stateProvider, formlyConfigProvider) {
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
        }, {
            title: 'Exceptions',
            sref: 'exceptions',
            icon: 'exclamation-triangle'
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

        .state('deployment', {
            url: '/deployments/:name',
            templateUrl: 'templates/deployment.html',
            controller: 'DeploymentDetailController as deploymentCtrl',
            resolve: {
                components: ["HUBClientService", function(HUBClientService) {
                    return HUBClientService.Component.query();
                }]
            }
        })
        .state('deployments.deployment.status', {
            url: '/:name/status',
            templateUrl: 'templates/deployment-status.html',
            controller: 'DeploymentStatusController as depStatusCtrl',
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
        })
        .state('exceptions', {
            url: '/exceptions',
            templateUrl: 'templates/exceptions.html',
            controller: 'ExceptionsController as excsCtrl',
            resolve: {}
        })
        .state('exception', {
            url: '/exceptions/:hash',
            templateUrl: 'templates/exception.html',
            controller: 'ExceptionController as excCtrl',
            resolve: {}
        });

    }
    config.$inject = ["sidebarSectionsProvider", "uiSelectConfig", "$urlRouterProvider", "$translateProvider", "$stateProvider", "formlyConfigProvider"];
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

    var LDAP_SCOPES = [{
        name: "SCOPE_SUBTREE",
        value: "SCOPE_SUBTREE"
    }, {
        name: "SCOPE_ONELEVEL",
        value: "SCOPE_ONLEVEL"
    }];

    function baseInput(type, name, label, placeholder, default_value, classname) {
        return {
            key: name,
            type: 'input',
            defaultValue: default_value,
            className: classname,
            templateOptions: {
                type: type,
                label: label,
                placeholder: placeholder
            }
        };
    }

    function textInput(name, label, placeholder, default_value, classname) {
        return baseInput('input', name, label, placeholder, default_value, classname);
    }

    function passwordInput(name, label, placeholder, default_value, classname) {
        return baseInput('password', name, label, placeholder, default_value, classname);
    }

    function titleSeparator(title) {
        return {
            "template": '<hr /><div class="fieldgroup-title"><strong>' + title + '</strong></div>'
        };
    }

    function checkboxInput(name, label, classname) {
        return {
            key: name,
            type: 'checkbox',
            className: classname,
            templateOptions: {
                label: label
            }
        };
    }

    function selectInput(name, label, options, classname) {
        return {
            key: name,
            type: "select",
            className: classname,
            templateOptions: {
                label: label,
                options: options
            }
        };
    }

    function fieldGroup(fields) {
        return {
            className: "display-flex",
            fieldGroup: fields
        };
    }

    angular
        .module('hub')
        .value('ComponentSchemas', {

            mongodbreplicamember: [
                fieldGroup([
                    textInput('name', 'Component Identifier', '', 'mongocluster', 'flex-1'),
                    textInput('title', 'Component Description', '', '', 'flex-1')
                ]),
                titleSeparator('Setup parameters:'),
                textInput('path', 'Setup path', '', '/var/mongodb', ''),
                fieldGroup([
                    textInput('server', 'Server where is installed', '', '', 'flex-2'),
                    textInput('host', 'Effective dns of member', '', '', 'flex-2'),
                    textInput('port', 'port', '', '27001', 'flex-1')
                ])

            ],

            ldapserver: [
                fieldGroup([
                    textInput('name', 'Component Identifier', '', 'mongocluster', 'flex-1'),
                    textInput('title', 'Component Description', '', '', 'flex-1')
                ]),
                titleSeparator('Server parameters:'),
                fieldGroup([
                    textInput('server', 'LDAP server uri', 'ldaps://server:port', '', 'flex-1'),
                    checkboxInput('readonly', 'Do not write to this server', 'flex-1')
                ]),
                titleSeparator('Security settings:'),
                fieldGroup([
                    textInput('admin_dn', 'LDAP bind dn', '', '', 'flex-1'),
                    textInput('admin_password', 'LDAP bind password', '', '', 'flex-1')
                ]),
                titleSeparator('Search parameters:'),
                fieldGroup([
                    textInput('users_base_dn', 'Base DN where users live', '', '', 'flex-2'),
                    selectInput('user_scope', 'Scope to search', LDAP_SCOPES, 'flex-1')
                ]),
                fieldGroup([
                    textInput('group_base_dn', 'Base DN where users live', '', '', 'flex-2'),
                    selectInput('group_scope', 'Scope to search', LDAP_SCOPES, 'flex-1')
                ])
            ],

            mongodbcluster: [
                fieldGroup([
                    textInput('name', 'Component Identifier', '', 'mongocluster', 'flex-1'),
                    textInput('title', 'Component Description', '', '', 'flex-1')
                ]),
                textInput('replicaset', 'Replicaset name for this cluster', '', '', 'input-small'),
                titleSeparator('Security settings:'),
                fieldGroup([
                    textInput('root_username', 'Mongodb "root" user', '', 'root', 'flex-1'),
                    passwordInput('root_password', 'Mongodb "root" password', 'password', '', 'flex-1')
                ]),
                fieldGroup([
                    textInput('db_username', 'Mongodb databases administrator user', '', 'admin', 'flex-1'),
                    passwordInput('db_password', 'Mongodb databases administrator password', 'password', '', 'flex-1')
                ]),
                textInput('admindb', 'Name of the database used for global authentication,\n leave blank to authenticate directly on working database.', '', '', 'input-small')
            ]
        });

})();

(function() {
    'use strict';

    angular
        .module('hub')
        .controller('ExceptionsController', ExceptionsController);

    /**
     * @desc
     */
    /* @nInject */
    function ExceptionsController(HUBClientService) {
        var self = this;
        self.exceptions = HUBClientService.Exception.query();

        self.remove = remove;

        /////////////////////

        function remove(exception) {
            HUBClientService.Exception.remove({hash: exception.id}, function () {
                self.exceptions = HUBClientService.Exception.query();
            }, function () {
                //
            });
        }
    }
    ExceptionsController.$inject = ["HUBClientService"];

})();

/* global Prism */
(function() {
    'use strict';

    angular
        .module('hub')
        .controller('ExceptionController', ExceptionController);

    /**
     * @desc
     */
    /* @nInject */
    function ExceptionController($stateParams, HUBClientService) {
        var self = this;
        self.hash = $stateParams.hash;
        self.exception = HUBClientService.Exception.get({hash: self.hash});
        self.request = '';
        self.exception.$promise.then(function(data) {
          self.request = Prism.highlight(data.request, Prism.languages.http);
          self.traceback = Prism.highlight(data.traceback, Prism.languages.python);
        });
    }
    ExceptionController.$inject = ["$stateParams", "HUBClientService"];

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
    function DeploymentsListController($cookies, $modal, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, HUBClientService) {
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

        self.deployments = HUBClientService.Deployment.query();

    }
    DeploymentsListController.$inject = ["$cookies", "$modal", "DTOptionsBuilder", "DTTranslations", "DTColumnDefBuilder", "HUBClientService"];

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
        .module('hub')
        .controller('DeploymentDetailController', DeploymentDetailController)
        .controller('NewComponentCtrl', NewComponentCtrl);

    /**
     * @desc
     */
    /* @nInject */
    function DeploymentDetailController($cookies, $filter, $modal, $stateParams, components, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, HUBClientService) {
        var self = this;

        self.obj = HUBClientService.Deployment.get({
            name: $stateParams.name
        });

        self.selectedComponent = {};
        self.components = components;
        self.selectedComponent = self.components[0];

        self.newComponentModal = newComponentModal;
        self.newSubcomponentModal = newSubcomponentModal;
        self.availableSubcomponents = availableSubcomponents;

        /////////////////////////////

        function availableSubcomponents(componentType) {
            return $filter('filter')(self.components, {type:componentType}, true)[0].components;
        }

        function newComponentModal() {
            var modalInstance = $modal.open({
                templateUrl: 'templates/new-component.html',
                controller: 'NewComponentCtrl as newCompCtrl',
                resolve: {
                    component_type: function() {
                        return self.selectedComponent;
                    },
                    deployment_name: function() {
                        return self.obj.name;
                    },
                    parent_component: function() {
                        return undefined;
                    }

                }
            });
            modalInstance.result.then(function() {
                self.obj = HUBClientService.Deployment.get({
                    name: $stateParams.name
                });
            }, function() {

            });

        }

        function newSubcomponentModal(component, subcomponent) {
            var modalInstance = $modal.open({
                templateUrl: 'templates/new-component.html',
                controller: 'NewComponentCtrl as newCompCtrl',
                resolve: {
                    component_type: function() {
                        return subcomponent;
                    },
                    deployment_name: function() {
                        return self.obj.name;
                    },
                    parent_component: function() {
                        return component;
                    }
                }
            });
            modalInstance.result.then(function() {
                self.obj = HUBClientService.Deployment.get({
                    name: $stateParams.name
                });
            }, function() {

            });

        }
    }
    DeploymentDetailController.$inject = ["$cookies", "$filter", "$modal", "$stateParams", "components", "DTOptionsBuilder", "DTTranslations", "DTColumnDefBuilder", "HUBClientService"];

    /**
     * @desc
     */
    /* @nInject */
    function NewComponentCtrl($modalInstance, ComponentSchemas, HUBClientService, component_type, deployment_name, parent_component) {
        var self = this;
        self.model = {};
        self.component_type = component_type;
        self.formFields = ComponentSchemas[component_type.type];
        self.onSubmit = onSubmit;
        self.onCancel = onCancel;

        /////////////////////////

        function onSubmit() {
            var name = self.model.name;
            var title = self.model.title;
            delete self.model.name;
            delete self.model.title;

            var new_component = {
                    'component': self.component_type.type,
                    'name': name,
                    'title': title,
                    'params': self.model
                };
            if (parent_component) {
                new_component.parent = parent_component.name;
            }

            HUBClientService.DeploymentComponent.save({
                    name: deployment_name
                }, new_component,
                function(data) {
                    $modalInstance.close(data);
                },
                function() {
                    //fail
                });
        }

        function onCancel() {
            $modalInstance.dismiss('cancel');
        }

    }
    NewComponentCtrl.$inject = ["$modalInstance", "ComponentSchemas", "HUBClientService", "component_type", "deployment_name", "parent_component"];

})();

(function() {
    'use strict';

    angular
        .module('hub')
        .controller('DeploymentStatusController', DeploymentStatusController);

    /**
     * @desc
     */
    /* @nInject */
    function DeploymentStatusController(HUBClientService) {
        var self = this;
    }
    DeploymentStatusController.$inject = ["HUBClientService"];

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
        this.Component = $resource(
            hubInfo.server + '/api/components/:name',
            null,
            {
                query: {method:'GET', isArray: true, headers:hubInfo.headers},
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

        this.DeploymentComponent = $resource(
            hubInfo.server + '/api/deployments/:name/components',
            null,
            {
                save: {method:'POST', headers:hubInfo.headers}
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
