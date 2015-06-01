(function() {
    'use strict';

    angular.module('hub.domain', [
        'datatables',
        'datatables.bootstrap',
        'ui.bootstrap',
        'ui.router',
        'ui.select',
        'ui.jq',
        'ui.slimscroll',
        'ngSanitize',
        'ngCookies',
        'pascalprecht.translate',
        'puElasticInput',
        'ngJsonExplorer',
        'btford.markdown',

        'hub.sidebar',
        'hub.client',
        'max.client',
        'hub.users',
        'hub.contexts'
    ]);

})();

(function() {
    'use strict';

    angular
        .module('hub.domain')
        .controller('ApiController', ApiController)
        .controller('EndpointController', EndpointController);

    /**
     * @desc
     */
    /* @nInject */
    function ApiController() {
        var self = this;
        self = self;
    }

    /**
     * @desc
     */
    /* @nInject */
    function EndpointController($http, $state, $stateParams, MAXInfo, EndpointsService) {
        var self = this;

        var route = $stateParams.endpoint;
        var current = EndpointsService.getEndpoint(route);

        // Default values for current endpoint data
        self.name = current.route_name;
        self.route = routeParts(current.route_url);
        self.info = MAXInfo.headers;

        // Model to store POST PUT payloads
        self.data = undefined;

        // Model to store the values for the inputs of the rest variable parts
        self.rest_params = {};

        // Model to store the response content
        self.response = {
          placeholder: 'No response yet, <br/>launch a request first.'
        };

        // Model to control display of the endpoint view error message
        self.error = {
          active: false,
          message: 'Error message'
        };

        // Controls the current and initialstate of the toggable sections
        self.visibility = {
          modifiers: false,
          headers: false,
          documentation: false
        };

        // Default values and state of the elements on Modifiers section
        self.modifiers = {
            limit: {
                enabled:false,
                value:10,
                available:true,
                type: 'text'
            },
            sort: {
                enabled:false,
                value: 'published',
                options: ['published', 'likes', 'flagged'],
                available:true,
                type: 'select'
            },
            priority: {
                enabled:false,
                value: 'activity',
                options: ['activity', 'comments'],
                available:true,
                type: 'select'
            },
            before: {
                enabled:false,
                value:'',
                available:true,
                type: 'text'
            },
            after: {
                enabled:false,
                value:'',
                available:true,
                type: 'text'
            },
            notifications: {
                enabled:false,
                value:'0',
                available:true,
                type: 'text'
            }

        };


        var status = resolveActiveMethod();
        if (status.redirect) {
            gotoMethod(status.method);
        } else {
            setActiveMethod(status.method);
            self.url = forgeURL();

        }

        //////////////////////////////////////

        self.isActiveMethod = isActiveMethod;
        self.gotoMethod = gotoMethod;
        self.setActiveMethod = setActiveMethod;
        self.routeParts = routeParts;
        self.showError = showError;
        self.hideError = hideError;
        self.renderResponse = renderResponse;
        self.forgeURL = forgeURL;
        self.launch = launch;
        self.toggle = toggle;
        self.resolveActiveMethod = resolveActiveMethod;


        /**
         * @desc Load the methods implemented for the current resource.
         *       self.methods will hold the object representing each method
         *       self.available methods will hold a list of the implemented ones names
         *       This last var is mainly used to determine the method that will be active
         *       in the ui by default
         */
        function resolveActiveMethod() {
            self.methods = [];
            self.available_methods = [];
            angular.forEach(['GET', 'POST', 'PUT', 'DELETE', 'HEAD'], function(method, key) {
               var method_state = {name:method, implemented: current.methods[method] === undefined ? false : true};
               if (current.methods[method] !== undefined) {
                  self.available_methods.push(method);
               }
               this.push(method_state);
            }, self.methods);

            var first_available_method = self.available_methods[0];
            var requested_method = $stateParams.method ? $stateParams.method.toUpperCase(): first_available_method;
            var selected_method = _.contains(self.available_methods, requested_method) ? requested_method: first_available_method
            return {
                method: selected_method,
                redirect: selected_method !== requested_method
            };
        }

        /**
         * @desc Returns a class if the checked method is the active one
         * @returns {Boolean}
         */
        function isActiveMethod(method) {
          return method === self.active_method ? 'active': '';
        }

        /**
         * @desc
         */
        function gotoMethod(method) {
              $state.go('api.method', {endpoint: $stateParams.endpoint, method: method.toLowerCase()})
        }

        /**
         * @desc
         */

        function setActiveMethod(method) {
          self.active_method = method;
          self.data = method === 'PUT' | method === 'POST' ? current.methods[self.active_method].payload : undefined;
          self.description = current.methods[self.active_method].description;
          self.documentation = current.methods[self.active_method].documentation;
          var available_method_modifiers = current.methods[self.active_method].modifiers;
          self.has_modifiers = !_.isEmpty(available_method_modifiers);
          self.modifiers_toggle_message = self.has_modifiers ? '(Toggle section to see available modifiers)' : 'No modifiers available';
          angular.forEach(self.modifiers, function(modifier, key) {
              self.modifiers[key].available = _.contains(available_method_modifiers, key);
          });
        }

        /**
         * @desc
         */
        function routeParts(route_url) {
            var parts = route_url.match(/[^\/]+/g);
            var destination = [];
            _.each(parts, function(element, index, list) {
               if (element[0] === '{') {
                var element_name = element.match(/\{(.*?)\}/)[1];
                // Set separators on 1+ segments
                if (index > 0) {
                    // Include / separator at the end of the last segment
                    if (_.last(destination).fixed) {
                        _.last(destination).text += '/';
                    // Append a fixed / part if last segment was a param
                    } else {
                        destination.push({'text': '/', fixed:true, param:false});
                    }
                }
                //Add the param element
                destination.push({'text': element, fixed:false, param:true, name:element_name});

               } else {
                var newpart = '/' + element;
                if (index === 0) {
                    destination.push({'text': newpart, fixed:true, param:false});
                } else {
                    // join together the current ant the last part ig both fixed
                    if (_.last(destination).fixed) {
                        _.last(destination).text += newpart;
                    // Otherwise add the new fixed part
                    } else {
                        destination.push({'text': newpart, fixed:true, param:false});
                    }
                }

               }
          });
          return destination;
        }

        /**
         * @desc
         */
        function showError(message) {
          self.error.active = true;
          self.error.message = message;
        }

        /**
         * @desc
         */
        function hideError() {
          self.error.active = false;
        }

        /**
         * @desc
         */
        function renderResponse(data, status, headers, config, finishTime) {
            var statuses = {
              200: 'Ok',
              400: 'Bad Request',
              401: 'Unauthorized',
              403: 'Forbidden',
              404: 'Not Found'
            };

            var json_data = angular.fromJson(data);
            self.response.raw = data;
            self.response.placeholder = '';
            self.response.json = json_data;
            self.response.status = status + ' '+ statuses[status];
            self.response.type = status >= 200 && status < 400 ? 'success' : 'failure';
            var time = finishTime - self.requestStartTime;
            self.response.time = "(" + time + " ms)";

        }

        /**
         * @desc
         */
        function forgeURL() {

            // Prepare path part of the url filling in the supplied
            // rest parameters into the route gaps
            var url_path = '';
            var missing_or_empty_params = false;
            angular.forEach(self.route, function(route_segment, key) {
                if (route_segment.fixed) {
                    url_path += route_segment.text;
                } else {
                    var segment_value = self.rest_params[route_segment.name];
                    var empty = segment_value === undefined | segment_value === '';
                    missing_or_empty_params = missing_or_empty_params && empty;
                    url_path += segment_value === undefined ? '' : segment_value;
                }
            }, url_path);

            // Prepare the query string part of the url using only
            // the enabled ones
            var qs_enabled = {};
            angular.forEach(self.modifiers, function(qs_param, key) {
              if (qs_param.enabled && !_.isEmpty(qs_param.value)) {
                qs_enabled[key] = qs_param.value;
              }
            }, qs_enabled);
            var qs = _.isEmpty(qs_enabled) ? '' : '?' + jQuery.param(qs_enabled);

            // Forge final url combining all parts
            var endpoint_url = MAXInfo.max_server + url_path +  qs;

            self.url = endpoint_url;
            return endpoint_url;
        }

        /**
         * @desc
         */
        function launch() {
            self.hideError();
            var missing_or_empty_params = false;
            var endpoint_url = self.forgeURL();

            if (missing_or_empty_params) {
              self.showError('Some parameters missing on destination url');
              return;
            }

            var request = {
              url: endpoint_url,
              method: self.active_method,
              headers: MAXInfo.headers
            };

            if (self.active_method === 'POST' | self.active_method === 'PUT') {
              request.data = angular.fromJson(self.data);
            }

            self.requestStartTime =  new Date().getTime();
            $http(request)
            .success(function(data, status, headers, config) {
                var requestFinishTime = new Date().getTime();
                self.renderResponse(data, status, headers, config, requestFinishTime);
            })
            .error(function(data, status, headers, config) {
                var requestFinishTime = new Date().getTime();
                self.renderResponse(data, status, headers, config, requestFinishTime);
            });
        }

        /**
         * @desc
         */
        function toggle(section) {
          self.visibility[section] = !self.visibility[section];
        }

    }
    EndpointController.$inject = ["$http", "$state", "$stateParams", "MAXInfo", "EndpointsService"];

})();


(function() {
    'use strict';

    angular
        .module('hub.domain')
        .factory('EndpointsService', EndpointsService);

    /**
     * @desc
     */
    /* @nInject */
    function EndpointsService($state, $q, sidebarSections, MAXClientService) {
        var endpoints_by_category = {};
        var endpoints = {};

        return {
            loadEndpoints: loadEndpoints,
            getEndpoint: getEndpoint
        };


        function loadEndpoints() {
              var deferred = $q.defer();
              endpoints_by_category = MAXClientService.ApiInfo.by_category();
              endpoints_by_category.$promise.then(function(data) {
                  endpoints_by_category = data;
                  var categories = [];
                  angular.forEach(data, function(category, key) {
                      var subsection = {title: category.name};
                      var thirdlevel = [];
                      angular.forEach(category.resources, function(resource, key) {
                         endpoints[resource.route_id] = resource;
                         endpoints[resource.route_id].category = category.name;
                         var url = $state.href('api.endpoint', {endpoint: resource.route_id});
                         this.push({title: resource.route_name, sref: url});
                      }, thirdlevel);

                      subsection.subsections = thirdlevel;
                      subsection.sref = 'api.' + subsection.title;
                      this.push(subsection);
                  }, categories);

                  sidebarSections.subsection('api', categories);
                  deferred.resolve(data);
              });
              return deferred.promise;
        }

        function getEndpoint(endpoint) {
            return endpoints[endpoint];
        }
    }
    EndpointsService.$inject = ["$state", "$q", "sidebarSections", "MAXClientService"];


})();

/* global Prism */
(function() {
    'use strict';

    angular
        .module('hub.domain')
        .controller('ExceptionController', ExceptionController);

    /**
     * @desc
     */
    /* @nInject */
    function ExceptionController($stateParams, MAXClientService) {
        var self = this;
        self.hash = $stateParams.id;
        self.exception = MAXClientService.Exception.get({id: self.hash});
        self.request = '';
        self.exception.$promise.then(function(data) {
          self.request = Prism.highlight(data.request, Prism.languages.http);
          self.traceback = Prism.highlight(data.traceback, Prism.languages.python);
        });
    }
    ExceptionController.$inject = ["$stateParams", "MAXClientService"];

})();

(function() {
    'use strict';

    angular
        .module('hub.domain')
        .controller('ExceptionsController', ExceptionsController);

    /**
     * @desc
     */
    /* @nInject */
    function ExceptionsController(MAXClientService) {
        var self = this;
        self.exceptions = MAXClientService.Exception.query();
    }
    ExceptionsController.$inject = ["MAXClientService"];
})();

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
                endpoints: ["EndpointsService", function(EndpointsService) {
                    return EndpointsService.loadEndpoints();
                }]
            }
        })

        // This state actually acts as a redirection to the first
        // available method of the endpoint, using api.method state
        .state('api.endpoint', {
            url: '/:endpoint',
            templateUrl: 'templates/api.method.html',
            controller: 'EndpointController as endpointCtrl',
            resolve: {
                expanded: ["$stateParams", "sidebarSections", "endpoints", "EndpointsService", function($stateParams, sidebarSections, endpoints, EndpointsService) {
                    var current_category = EndpointsService.getEndpoint($stateParams.endpoint).category;
                    sidebarSections.expand('api', 'section', true);
                    sidebarSections.expand('api.' + current_category, 'subsection', true);
                    return;
                }]
            }

        })

        .state('api.method', {
                url: '/:endpoint/:method',
                templateUrl: 'templates/api.method.html',
                controller: 'EndpointController as endpointCtrl',
                resolve: {
                    expanded: ["$stateParams", "sidebarSections", "endpoints", "EndpointsService", function($stateParams, sidebarSections, endpoints, EndpointsService) {
                        var current_category = EndpointsService.getEndpoint($stateParams.endpoint).category;
                        sidebarSections.expand('api', 'section', true);
                        sidebarSections.expand('api.' + current_category, 'subsection', true);
                        return;
                    }]
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
    config.$inject = ["sidebarSectionsProvider", "$stateProvider", "$urlRouterProvider", "$translateProvider", "uiSelectConfig"];
})();

(function() {
    'use strict';

    angular
        .module('hub.domain')
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

(function() {
    'use strict';

    angular
        .module('hub.domain')
        .controller('MainAppController', MainAppController);


    /**
     * @desc
     */
    /* @nInject */
    function MainAppController($stateParams, $cookies, $translate, sidebarSections, hubSession, MAXSession, HUBClientService) {
        var self = this;
        var domainName = hubSession.domain;
        $cookies.currentDomain = $stateParams.domain;
        self.domainObj = HUBClientService.Domain.get({
                id: domainName
            },
            function(response) {},
            function(response) {
                self.error = 'Request to ' + response.config.url + ' failed with code ' + response.status + '.<br/> Server responded: "' + response.data.error_description + '"'

            }
        );
        self.sidebar_status = '';
        self.maxuisettings = {
            generatorName: "uLearn HUB",
            language: "ca",
            oAuthGrantType: "password",
            avatarURLpattern: MAXSession.max_server + "/people/{0}/avatar",
            profileURLpattern: "#",
            username: MAXSession.username,
            oAuthToken: MAXSession.oauth_token,
            maxServerURL: MAXSession.max_server,
            maxServerURLAlias: MAXSession.max_server,
            maxTalkURL: MAXSession.max_server + "/stomp"
        };

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
    MainAppController.$inject = ["$stateParams", "$cookies", "$translate", "sidebarSections", "hubSession", "MAXSession", "HUBClientService"];
})();

(function() {
    'use strict';

    angular
        .module('hub.domain')
        .controller('LanguageSelectorController', LanguageSelectorController);

    /**
     * @desc
     */
    /* @nInject */
    function LanguageSelectorController($cookies, $translate, $state) {
        var self = this;
        var valid_cookie_language = $cookies.currentLang === 'ca';
        self.currentLang = {
            code: $cookies.currentLang === undefined ? 'ca' : $cookies.currentLang
        };
        self.languages = [{
            code: 'ca',
            name: 'Català'
        }, {
            code: 'es',
            name: 'Castellano'
        }, {
            code: 'en',
            name: 'English'
        }];

        self.changeLanguage = changeLanguage;

        /////////////////////////////

        function changeLanguage (){
            $translate.use(self.currentLang.code);
            $cookies.currentLang = self.currentLang.code;
            $state.go('domain', {
                domain: $cookies.currentDomain
            });
        }
    }
    LanguageSelectorController.$inject = ["$cookies", "$translate", "$state"];
})();

(function() {
    'use strict';

    angular
        .module('hub.users', [
    ]);

})();

(function() {
    'use strict';

    angular
        .module('hub.users')
        .controller('ModalInstanceCtrl', ModalInstanceCtrl)
        .controller('ModalDeleteUser', ModalDeleteUser)
        .controller('ModalUnsubscribeContext', ModalUnsubscribeContext);

    /**
     * @desc
     */
    /* @nInject */
    function ModalInstanceCtrl($scope, $modalInstance, MAXClientService, items) {
        $scope.alerts = [];
        $scope.ok = function() {
            MAXClientService.User.save($scope.newuser)
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
    ModalInstanceCtrl.$inject = ["$scope", "$modalInstance", "MAXClientService", "items"];


    /**
     * @desc
     */
    /* @nInject */
    function ModalDeleteUser($scope, $modalInstance, MAXClientService, items) {
        $scope.alerts = [];

        var username = items;
        $scope.ok = function() {
            MAXClientService.User.remove({
                    id: username
                })
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
    ModalDeleteUser.$inject = ["$scope", "$modalInstance", "MAXClientService", "items"];


    /**
     * @desc
     */
    /* @nInject */
    function ModalUnsubscribeContext($scope, $modalInstance, MAXClientService, items) {
        $scope.alerts = [];
        var username = items[0];
        var hash = items[1];
        $scope.ok = function() {
            MAXClientService.UserSubscription.remove({
                    id: username,
                    hash: hash
                })
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
    ModalUnsubscribeContext.$inject = ["$scope", "$modalInstance", "MAXClientService", "items"];



})();

(function() {
    'use strict';

    angular
        .module('hub.users')
        .controller('UserProfileController', UserManageController);

    /**
     * @desc
     */
    /* @nInject */
    function UserManageController($cookies, $scope, $stateParams, $modal, $log, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, MAXClientService, ContextPermissionsFactory) {

        var self = this;
        var lang = $cookies.currentLang;
        $scope.alerts = [];
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
        self.username = $stateParams.id;
        self.contextAvailable = MAXClientService.Context.query();
        MAXClientService.User.getUsu({
                id: self.username
            })
            .$promise.then(function(data) {
                self.user = data;
                var res = ContextPermissionsFactory.getToContextList(data);
                self.contextsList = res[0];
                self.urlList = res[1];
                self.user.large_avatar = 'http://localhost:8081/people/' + self.user.username + '/avatar/large';
            });

        self.refreshContextList = refreshContextList;
        self.changePermission = changePermission;
        self.saveUser = saveUser;
        self.closeAlert = closeAlert;
        self.addContextToUser = addContextToUser;
        self.unsubscribeContext = unsubscribeContext;

        //////////////////////////////////

        /**
         * @desc
         */
        function refreshContextList(search) {
            //Users search to add
            if (search !== '') {
                MAXClientService.User.query({
                        username: search
                    })
                    .$promise.then(function(data) {
                        self.contextAvailable = data;
                    });
            }
        }

        /**
         * @desc
         */
        function changePermission(hash, username, permission, state) {
            if (state === false) {
                MAXClientService.UserSubscriptionPermission.remove({
                    hash: hash,
                    iduser: username,
                    permission: permission
                });
            } else if (state === true) {
                MAXClientService.MAXClientService.UserSubscriptionPermission.update({
                    hash: hash,
                    iduser: username,
                    permission: permission
                });
            }
        }

        /**
         * @desc
         */
        function saveUser() {
            MAXClientService.User.update({
                    id: self.username
                }, self.user)
                .$promise.then(function(data) {
                    $scope.alerts.push({
                        type: 'success',
                        msg: 'User successfully saved'
                    });
                }, function(error) {
                    $scope.alerts.push({
                        type: 'danger',
                        msg: error.data.error + ': ' + error.data.error_description
                    });
                });
        }

        /**
         * @desc
         */
        function closeAlert(index) {
            $scope.alerts.splice(index, 1);
        }

        /**
         * @desc
         */
        function addContextToUser() {
            var contexts = self.contextsSelected;
            var username = self.username;
            for (var i = 0; i < contexts.length; i++) {
                var url = {
                    "objectType": "context",
                    "url": contexts[i].url
                };
                MAXClientService.UserSubscription.save({
                    id: username,
                    object: url
                });
            }
            MAXClientService.User.getUsu({
                    id: self.username
                })
                .$promise.then(function(data) {
                    self.user = data;
                    var res = ContextPermissionsFactory.getToContextList(data);
                    self.contextsList = res[0];
                    self.urlList = res[1];
                });
        }

        /**
         * @desc
         */
        function unsubscribeContext(size, username, contextHash) {
            var modalUnsubscribeInstance = $modal.open({
                templateUrl: 'unsubscribe-context.html',
                controller: 'ModalUnsubscribeContext',
                size: size,
                resolve: {
                    items: function() {
                        return [username, contextHash];
                    }
                }
            });
            modalUnsubscribeInstance.result.then(function(newcontext) {
                //aqui va el quitar del listado
                MAXClientService.User.getUsu({
                        id: self.username
                    })
                    .$promise.then(function(data) {
                        self.user = data;
                        var res = ContextPermissionsFactory.getToContextList(data);
                        self.contextsList = res[0];
                        self.urlList = res[1];
                    });
            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
        }
    }
    UserManageController.$inject = ["$cookies", "$scope", "$stateParams", "$modal", "$log", "DTOptionsBuilder", "DTTranslations", "DTColumnDefBuilder", "MAXClientService", "ContextPermissionsFactory"];
})();

(function() {
    'use strict';

    angular
        .module('hub.users')
        .controller('UsersRolesController', UsersRolesController);

    /**
     * @desc
     */
    /* @nInject */
    function UsersRolesController($cookies, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, MAXClientService) {
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
        self.users = MAXClientService.SecurityUsers.query();

        self.changeRole = changeRole;

        //////////////////////////////

        /**
         * @desc
         */
        function changeRole(state, rolename, username) {
            if (state === true) {
                MAXClientService.SecurityUserRole.save({
                    idrol: rolename,
                    iduser: username
                });
            }
            if (state === false) {
                MAXClientService.SecurityUserRole.remove({
                    idrol: rolename,
                    iduser: username
                });
            }
        }
    }
    UsersRolesController.$inject = ["$cookies", "DTOptionsBuilder", "DTTranslations", "DTColumnDefBuilder", "MAXClientService"];

})();

(function() {
    'use strict';

    angular
        .module('hub.users')
        .controller('UserListController', UserListController);

    /**
     * @desc
     */
    /* @nInject */
    function UserListController($cookies, $modal, $log, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, MAXClientService) {
        var self = this;
        var lang = $cookies.currentLang;

        self.search_text = '';

        // Default datatable options

        self.dtOptions = DTOptionsBuilder
            .newOptions().withPaginationType('simple').withDisplayLength(20)
            .withBootstrap()
            .withLanguage(DTTranslations[lang]);

        self.dtColumnDefs = [
            DTColumnDefBuilder.newColumnDef(0),
            DTColumnDefBuilder.newColumnDef(1),
            DTColumnDefBuilder.newColumnDef(2)
        ];

        self.users = [];

        self.search = search;
        self.openModal = openModal;
        self.confirmModal = confirmModal;

        //////////////////////////////////////////////

        /**
         * @desc
         */
        function search() {
            self.users = MAXClientService.User.query({
                username: self.search_text,
                limit: 0
            });
        }

        /**
         * @desc
         */
        function openModal(size) {
            var modalInstance = $modal.open({
                templateUrl: 'new-user.html',
                controller: 'ModalInstanceCtrl',
                size: size,
                resolve: {
                    items: function() {
                        return [];
                    }
                }
            });
            modalInstance.result.then(function(newuser) {
                self.users.push(newuser);
            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
        }

        /**
         * @desc
         */
        function confirmModal(size, username) {
            var modalDeleteInstance = $modal.open({
                templateUrl: 'remove-user.html',
                controller: 'ModalDeleteUser',
                size: size,
                resolve: {
                    items: function() {
                        return username;
                    }
                }
            });
            modalDeleteInstance.result.then(function(username) {
                //aqui va el quitar del listado
                for (var i = 0; i < self.users.length; i += 1) {
                    if (self.users[i].username === username) {
                        self.users.slice(i);
                    }
                }
            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
        }

    }
    UserListController.$inject = ["$cookies", "$modal", "$log", "DTOptionsBuilder", "DTTranslations", "DTColumnDefBuilder", "MAXClientService"];
})();

(function() {
    'use strict';

    angular
        .module('hub.contexts', [
    ]);

})();

(function() {
    'use strict';

    angular
        .module('hub.contexts')
        .controller('ContextDetailsController', ContextDetailsController);

    /**
     * @desc
     */
    /* @nInject */
    function ContextDetailsController($scope, $state, $modal, $cookies, $stateParams, $log, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, MAXClientService, ContextPermissionsFactory) {
        var self = this;
        $scope.alerts = [];
        self.usersList = [];
        self.usernameList = [];
        self.usersSelected = [];
        self.usersAvailable = [];
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

        self.contexts = MAXClientService.Context.query();

        self.application_url = '';
        self.contextHash = $stateParams.id;

        if (self.newHash) {
            self.contextHash = self.newHash;
        }

        MAXClientService.Context.get({
                id: self.contextHash
            })
            .$promise.then(function(dataContext) {
                self.context = dataContext;
                //Get context users Subscribers
                MAXClientService.ContextSubscriptions.query({
                        hash: self.context.hash
                    })
                    .$promise.then(function(data) {
                        var res = ContextPermissionsFactory.getToUsersList(data, self.context.hash);
                        self.usersList = res[0];
                        self.usernameList = res[1];
                    });

            });

        self.refreshUsersList = refreshUsersList;
        self.onSelect = onSelect;
        self.changePermission = changePermission;
        self.saveContext = saveContext;
        self.addUsersToContext = addUsersToContext;
        self.unsubscribeUser = unsubscribeUser;

        //////////////////////////////////////

        /**
         * @desc
         */
        function refreshUsersList(search) {
            //Users search to add
            if (search !== '') {
                MAXClientService.User.query({
                        username: search
                    })
                    .$promise.then(function(allUsers) {
                        self.usersAvailable = allUsers;

                    });
            }
        }

        /**
         * @desc
         */
        function onSelect($item, $select) {
            for (var i = 0; i < $select.selected.length; i++) {
                if ((self.usernameList.indexOf($select.selected[i].username)) > 0) {
                    $select.removeChoice(i);
                }
            }
        }

        /**
         * @desc
         */
        function changePermission(hash, username, permission, state) {

            if (state === false) {
                MAXClientService.UserSubscriptionPermission.remove({
                    hash: hash,
                    iduser: username,
                    permission: permission
                });
            } else if (state === true) {
                MAXClientService.UserSubscriptionPermission.update({
                    hash: hash,
                    iduser: username,
                    permission: permission
                });
            }

        }

        /**
         * @desc
         */
        function saveContext() {
            MAXClientService.Context.update({
                    id: self.contextHash
                }, self.context)
                .$promise.then(function(data) {
                    var newHash = data.hash;
                    $scope.alerts.push({
                        type: 'success',
                        msg: 'Context successfully saved'
                    });

                    $state.go('context', {
                        id: newHash
                    });

                }, function(error) {
                    $scope.alerts.push({
                        type: 'danger',
                        msg: error.data.error + ': ' + error.data.error_description
                    });
                });
        }

        /**
         * @desc
         */
        $scope.closeAlert = function(index) {
            $scope.alerts.splice(index, 1);
        };

        /**
         * @desc
         */
        function addUsersToContext() {
            var users = self.usersSelected;
            var url = {
                "objectType": "context",
                "url": self.context.url
            };
            for (var i = 0; i < users.length; i++) {
                MAXClientService.UserSubscription.save({
                    id: users[i].username,
                    object: url
                });

            }

            MAXClientService.ContextSubscriptions.query({
                    hash: self.context.hash
                })
                .$promise.then(function(data) {
                    var res = ContextPermissionsFactory.getToUsersList(data, self.context.hash);
                    self.usersList = res[0];
                    self.usernameList = res[1];
                });

        }

        /**
         * @desc
         */
        function unsubscribeUser(size, username, contextHash) {
            var modalUnsubscribeInstance = $modal.open({
                templateUrl: 'remove-user-context.html',
                controller: 'ModalUnsubscribeUser',
                size: size,
                resolve: {
                    items: function() {
                        return [username, contextHash];
                    }
                }
            });

            modalUnsubscribeInstance.result.then(function(newcontext) {
                //window.location.reload()
                MAXClientService.ContextSubscriptions.query({
                        hash: self.context.hash
                    })
                    .$promise.then(function(data) {
                        var res = ContextPermissionsFactory.getToUsersList(data, self.context.hash);
                        self.usersList = res[0];
                        self.usernameList = res[1];
                    });

            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
        }

    }
    ContextDetailsController.$inject = ["$scope", "$state", "$modal", "$cookies", "$stateParams", "$log", "DTOptionsBuilder", "DTTranslations", "DTColumnDefBuilder", "MAXClientService", "ContextPermissionsFactory"];
})();

(function() {
    'use strict';

    angular
        .module('hub.contexts')
        .controller('ContextListController', ContextListController);

    /**
     * @desc
     */
    /* @nInject */
    function ContextListController($cookies, $modal, $log, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, MAXClientService) {
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

        self.application_url = '';
        self.contexts = MAXClientService.Context.query({
            limit: 0
        });


        self.openModal = openModal;
        self.confirmModal = confirmModal;

        //////////////////////////////////////

        /**
         * @desc
         */
        function openModal(size) {

            var modalInstance = $modal.open({
                templateUrl: 'new-context.html',
                controller: 'ModalAddContext',
                size: size,
                resolve: {
                    items: function() {
                        return [];
                    }
                }
            });

            modalInstance.result.then(function(newcontext) {
                self.contexts.push(newcontext);

            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
        }

        /**
         * @desc
         */
        function confirmModal(size, hash) {
            var modalDeleteInstance = $modal.open({
                templateUrl: 'remove-context.html',
                controller: 'ModalDeleteContext',
                size: size,
                resolve: {
                    items: function() {
                        return hash;
                    }
                }
            });

            modalDeleteInstance.result.then(function(newcontext) {
                //aqui va el quitar del listado

            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
        }
    }
    ContextListController.$inject = ["$cookies", "$modal", "$log", "DTOptionsBuilder", "DTTranslations", "DTColumnDefBuilder", "MAXClientService"];

})();

(function() {
    'use strict';

    angular
        .module('hub.contexts')
        .controller('ModalAddContext', ModalAddContext)
        .controller('ModalDeleteContext', ModalDeleteContext)
        .controller('ModalUnsubscribeUser', ModalUnsubscribeUser);


    /**
     * @desc
     */
    /* @nInject */
    function ModalAddContext($scope, $modalInstance, MAXClientService) {
        $scope.alerts = [];

        $scope.ok = function() {
            MAXClientService.Context.save($scope.newcontext)
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
    ModalAddContext.$inject = ["$scope", "$modalInstance", "MAXClientService"];

    /**
     * @desc
     */
    /* @nInject */
    function ModalDeleteContext($scope, $modalInstance, Context, items) {
        $scope.alerts = [];

        var hash = items;
        $scope.ok = function() {
            Context.remove({
                    id: hash
                })
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
    ModalDeleteContext.$inject = ["$scope", "$modalInstance", "Context", "items"];


    /**
     * @desc
     */
    /* @nInject */
    function ModalUnsubscribeUser($scope, $modalInstance, UserSubscribe, items) {
        $scope.alerts = [];

        var username = items[0];
        var hash = items[1];

        $scope.ok = function() {
            UserSubscribe.remove({
                    id: username,
                    hash: hash
                })
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
    ModalUnsubscribeUser.$inject = ["$scope", "$modalInstance", "UserSubscribe", "items"];

})();

(function() {
    'use strict';

    angular
        .module('hub.contexts')
        .factory('ContextPermissionsFactory', ContextPermissionsFactory);

    /**
     * @desc
     */
    /* @nInject */
    function ContextPermissionsFactory() {
        return {
            getToContextList: getToContextList,
            getToUsersList: getToUsersList
        };

        //////////////////

        /**
         * @desc
         */
        function getToContextList(userObj) {
            var read = false;
            var write = false;
            var delet = false;
            var unsubscribe = false;
            var stringPermis = [];
            var contextsList = [];
            var urlList = [];

            if (userObj.subscribedTo) {
                for (var i = 0; i < userObj.subscribedTo.length; i++) {

                    for (var j = 0; j < userObj.subscribedTo[i].permissions.length; j++) {
                        stringPermis = userObj.subscribedTo[i].permissions[j];
                        if (stringPermis === 'read') {
                            read = true;
                        } else if (stringPermis === 'write') {
                            write = true;
                        } else if (stringPermis === 'unsubscribe') {
                            unsubscribe = true;
                        } else if (stringPermis === 'delete') {
                            delet = true;
                        }
                    }

                    contextsList.push({
                        displayName: userObj.subscribedTo[i].displayName,
                        url: userObj.subscribedTo[i].url,
                        hash: userObj.subscribedTo[i].hash,
                        permissionRead: read,
                        permissionWrite: write,
                        permissionUnsubscribe: unsubscribe,
                        permissionDelete: delet
                    });
                    urlList.push(userObj.subscribedTo[i].url);
                }

            }
        return [contextsList, urlList];
        }

        /**
        * @desc
        */
        function getToUsersList(userObj, contextHash) {

            var resuList = [];
            var usernameList = [];
            for (var i = 0; i < userObj.length; i++) {
                var read = false;
                var write = false;
                var delet = false;
                var unsubscribe = false;
                var stringPermis = [];


                for (var j = 0; j < userObj[i].permissions.length; j++) {
                    stringPermis = userObj[i].permissions[j];
                    if (stringPermis === 'read') {
                        read = true;
                    } else if (stringPermis === 'write') {
                        write = true;
                    } else if (stringPermis === 'unsubscribe') {
                        unsubscribe = true;
                    } else if (stringPermis === 'delete') {
                        delet = true;
                    }
                }
                resuList.push({
                    username: userObj[i].username,
                    permissionRead: read,
                    permissionWrite: write,
                    permissionUnsubscribe: unsubscribe,
                    permissionDelete: delet,
                    hash: contextHash
                });
                usernameList.push(userObj[i].username);
            }
            return [resuList, usernameList];
        }
    }
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
    }
    HUBClientService.$inject = ["$resource", "hubInfo"];
})();

(function() {
    'use strict';

    angular
        .module('max.client', [
            'ngResource'
    ]);

})();

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
    MAXClientService.$inject = ["$resource", "MAXInfo"];
})();

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
            controller: ["$scope", "$element", "$attrs", "MAXSession", function($scope, $element, $attrs, MAXSession) {
                MAXSession.username = $attrs.username;
                MAXSession.oauth_token = $attrs.oauthtoken;
                MAXSession.max_server = $attrs.maxserver;
            }]
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
    MAXInfo.$inject = ["MAXSession", "_MAXUI"];

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
