'use strict';

var ulearnhub = angular.module('uLearnHUB', [
    
    'hubClient',
    'maxClient',
    'datatables',
    'datatables.bootstrap',
    'ui.bootstrap',
    'ui.router',
    'ui.select',
    'ngSanitize',
    'ngCookies',
    'pascalprecht.translate'
]);

//ulearnhub.run(function(DTDefaultOptions) {
 //   DTDefaultOptions.setLanguageSource('locales/locale-es.json');
    //DTDefaultOptions.setLanguage({ sUrl: 'locales/locale-es.json'} );
//});


ulearnhub.config(['$stateProvider','$urlRouterProvider','$translateProvider','uiSelectConfig', function($stateProvider, $urlRouterProvider,$translateProvider,uiSelectConfig) {
    uiSelectConfig.theme = 'bootstrap';
    $urlRouterProvider.otherwise('/');

    $translateProvider.useStaticFilesLoader({
        prefix: 'locales/locale-',
        suffix: '.json'
    });

    $translateProvider.preferredLanguage('ca');

    
    $stateProvider
        
        // HOME STATES AND NESTED VIEWS ========================================
        .state('root', {
            url: '/',
            templateUrl: 'templates/root.html'
        })

        .state('domains', {
            url: '/domains',
            templateUrl: 'templates/domains.html',
            controller: 'DomainsController'
        })

        .state('domain', {
            url: '/domain/:domain',
            templateUrl: 'templates/domain.html',
            controller: 'DomainController',
        })

        .state('domain.users', {
            url: '/users',
            templateUrl: 'templates/users.html',
            controller: 'UsersManageController',
            resolve: {
               domain: function($stateParams, Domain, MAXSession, hubSession) {
                return setMaxSession($stateParams, Domain, MAXSession, hubSession); }
            }
        })

        .state('domain.contexts', {
            url: '/contexts',
            templateUrl: 'templates/contexts.html',
            controller: 'ContextsManageController',
            controllerAs:'contMan',
            resolve: {
               domain: function($stateParams, Domain, MAXSession, hubSession) {
                return setMaxSession($stateParams, Domain, MAXSession, hubSession); }
            }
        })

        .state('domain.user', {
            url: '/users/:id',
            templateUrl: 'templates/user.html',
            controller: 'UserManageController',
            resolve: {
               domain: function($stateParams, Domain, MAXSession, hubSession) {
                return setMaxSession($stateParams, Domain, MAXSession, hubSession); }
            }
        })

        .state('domain.context', {
            url: '/contexts/:id',
            templateUrl: 'templates/context.html',
            controller: 'ContextManageController',
            coontrollerAs: 'contEdit',
            resolve: {
               domain: function($stateParams, Domain, MAXSession, hubSession) {
                return setMaxSession($stateParams, Domain, MAXSession, hubSession); }
            }
        })
        
        // ABOUT PAGE AND MULTIPLE NAMED VIEWS =================================
        .state('about', {
            // we'll get to this in a bit       
        });
        
}]);

ulearnhub.controller('languageController', ['$translate','$cookies','$state', function($translate,$cookies,$state) {
    var self = this;
    
  self.changeLanguage = function (key) {
    $translate.use(key);
    $cookies.currentLang = key;
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



function setMaxSession(state, Domain, MAXSession, hubSession) {
    var domainName = state.domain;
    self.domainObj = Domain.get({id:domainName});

    return self.domainObj.$promise.then(function(data){
        MAXSession.username = hubSession.username;
        MAXSession.oauth_token = hubSession.token;
        MAXSession.max_server = data.server;
      });
   }




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