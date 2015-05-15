'use strict';

var max_exceptions = angular.module('uLearnHUBDomainManagement');

max_exceptions.controller('ExceptionsController', ['$cookies', 'Exception', 'MAXSession', function($cookies, Exception, MAXSession) {
    var self = this;
    self.exceptions = Exception.query();

}]);


max_exceptions.controller('ExceptionController', ['$stateParams', '$cookies', 'Exception', 'MAXSession', function($stateParams, $cookies, Exception, MAXSession) {
    var self = this;
    self.hash = $stateParams.id;
    self.exception = Exception.get({id: self.hash});

}]);
