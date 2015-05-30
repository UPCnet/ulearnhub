'use strict';

var ulearnhub = angular.module('hub.domain', [
    'hubClient',
    'sidebar',
    'maxClient',
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
    'btford.markdown'
]);


ulearnhub.config(['sidebarSectionsProvider', '$stateProvider','$urlRouterProvider','$translateProvider','uiSelectConfig', function(sidebarSectionsProvider, $stateProvider, $urlRouterProvider,$translateProvider,uiSelectConfig) {

    sidebarSectionsProvider.setSections([
        {title: 'Dashboard', sref: 'domain', icon: 'tachometer'},
        {title: 'Users', sref: 'users', icon: 'user'},
        {title: 'Contexts', sref: 'contexts', icon: 'map-marker'},
        {title: 'Api', sref: 'api', icon: 'paperclip'},
        {title: 'Exceptions', sref: 'exceptions', icon: 'exclamation-triangle'}
    ]);

    uiSelectConfig.theme = 'bootstrap';
    $urlRouterProvider.otherwise('/');

    $translateProvider.useStaticFilesLoader({
        prefix: 'locales/locale-',
        suffix: '.json'
    });

    $translateProvider.preferredLanguage('ca');


    $stateProvider

        // HOME STATES AND NESTED VIEWS ========================================

        .state('domain', {
            url: '',
            templateUrl: 'templates/domain.html',
            resolve: {
            }
        })

        .state('users', {
            url: '/users',
            templateUrl: 'templates/users.html',
            controller: 'UsersManageController as usersCtrl',
            resolve: {
            }
        })

        .state('users.roles', {
            url: '/roles',
            templateUrl: 'templates/users.roles.html',
            controller: 'UsersRolesController as userRol',
            resolve: {
            }
        })

        .state('contexts', {
            url: '/contexts',
            templateUrl: 'templates/contexts.html',
            controller: 'ContextsManageController as contextsCtrl',
            resolve: {
            }
        })

        .state('user', {
            url: '/users/:id',
            templateUrl: 'templates/user.html',
            controller: 'UserManageController as userCtrl',
            resolve: {
            }
        })

        .state('context', {
            url: '/contexts/:id',
            templateUrl: 'templates/context.html',
            controller: 'ContextManageController as contextCtrl',
            resolve: {
            }
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
            resolve: {
            }
        })

        .state('exception', {
            url: '/exceptions/:id',
            templateUrl: 'templates/exception.html',
            controller: 'ExceptionController as excCtrl',
            resolve: {
            }
        });

}]);


ulearnhub.controller('languageController', ['$translate','$cookies','$state', function($translate,$cookies,$state) {
    var self = this;
    var valid_cookie_language = $cookies.currentLang == 'ca'
    self.currentLang = {code: $cookies.currentLang == undefined ? 'ca': $cookies.currentLang}
    self.languages = [
        {code: 'ca', name: 'Català'},
        {code: 'es', name: 'Castellano'},
        {code: 'en', name: 'English'}
    ]

  self.changeLanguage = function () {
    $translate.use(self.currentLang.code);
    $cookies.currentLang = self.currentLang.code;
    $state.go('domain',{domain:$cookies.currentDomain});

  };


}]);


ulearnhub.factory('getUrl',function($location){

    var url_host = $location.host();
    var url_port = $location.port();
    var url_protocol = $location.protocol();
    return url_protocol+'://'+url_host+':'+url_port;
});

ulearnhub.factory('ContextPermissions',function(){
    return {
        getToContextList:function(userObj){
            var read = false;
            var write = false;
            var delet = false;
            var unsubscribe = false;
            var stringPermis = [];
            var contextsList = [];
            var urlList = [];

            if (userObj.subscribedTo){
                for (var i=0; i<userObj.subscribedTo.length; i++){

                    for (var j=0; j<userObj.subscribedTo[i].permissions.length; j++){
                      stringPermis = userObj.subscribedTo[i].permissions[j];
                      if (stringPermis == 'read'){read = true;}
                      else if (stringPermis == 'write'){write = true;}
                      else if (stringPermis == 'unsubscribe'){unsubscribe = true;}
                      else if (stringPermis == 'delete'){delet = true;}
                    }

                    contextsList.push({displayName:userObj.subscribedTo[i].displayName,
                    url:userObj.subscribedTo[i].url,
                    hash:userObj.subscribedTo[i].hash,
                    permissionRead:read,
                    permissionWrite:write,
                    permissionUnsubscribe:unsubscribe,
                    permissionDelete:delet});
                    urlList.push(userObj.subscribedTo[i].url);
                }

            }
                return [contextsList,urlList];

        },

        getToUsersList:function(userObj,contextHash){

            var resuList = [];
            var usernameList = [];
            for (var i=0; i<userObj.length; i++){
                var read = false;
                var write = false;
                var delet = false;
                var unsubscribe = false;
                var stringPermis = [];


                for (var j=0; j<userObj[i].permissions.length; j++){
                  stringPermis = userObj[i].permissions[j];
                  if (stringPermis == 'read'){read = true;}
                  else if (stringPermis == 'write'){write = true;}
                  else if (stringPermis == 'unsubscribe'){unsubscribe = true;}
                  else if (stringPermis == 'delete'){delet = true;}
                }
                resuList.push({username:userObj[i].username,
                                  permissionRead:read,
                                  permissionWrite:write,
                                  permissionUnsubscribe:unsubscribe,
                                  permissionDelete:delet,
                                  hash:contextHash});
                usernameList.push(userObj[i].username);
            }
            return [resuList,usernameList];
        }
    }
});



// function setMaxSession(state, Domain, MAXSession, hubSession) {
//     var domainName = state.domain;
//     self.domainObj = Domain.get({id:domainName});

//     return self.domainObj.$promise.then(function(data){
//         MAXSession.username = hubSession.username;
//         MAXSession.oauth_token = hubSession.token;
//         MAXSession.max_server = data['max'];
//       });
//    }




// ======= HACER UN SERVICIO PARA LLAMAR DESDE EL RESOLVE DE LOS STATE ======== //
/*ulearnhub.service('domainManager',function(state, Domain, MAXSession, hubSession){
    self = this;
    self.domainName = '';
    self.domainObj = undefined;
    debugger
    self.getDomainObj = function() {
        debugger
        if (state.domainName == self.domainName){
            return self.domainObj;
        }
        else{
            self.domainName = state.domain;
            return Domain.get({id:self.domainName}).$promise.then(function(data){
                    MAXSession.username = hubSession.username;
                    MAXSession.oauth_token = hubSession.token;
                    MAXSession.max_server = data.server;
                    self.domainObj = data;
                })
            }
        }

});*/


// angular-datatables custom translations
ulearnhub.value('DTTranslations', {
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


ulearnhub.controller('MainAppController', ['sidebarSections', '$stateParams','$modal', '$log', '$translate', 'Domain','MAXSession','hubSession', 'DTOptionsBuilder', 'DTColumnDefBuilder','$cookies', function(sidebarSections, $stateParams,$modal, $log, $translate, Domain,MAXSession,hubSession, DTOptionsBuilder, DTColumnDefBuilder,$cookies) {
    var self = this;
    var domainName = hubSession.domain;
    $cookies.currentDomain = $stateParams.domain;
    self.domainObj = Domain.get(
        {id:domainName},
        function(response) {},
        function(response) {
            self.error = 'Request to ' + response.config.url + ' failed with code ' + response.status + '.<br/> Server responded: "' + response.data.error_description+ '"'

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

  self.toggleSidebar = function() {
      var collapsed = sidebarSections.toggle();
      self.sidebar_status = collapsed ? '' : 'page-sidebar-toggled';
  };

  self.changeLanguage = function (key) {
    $translate.use(key);
  };
}]);

