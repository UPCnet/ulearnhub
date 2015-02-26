'use strict';

var ulearnhub = angular.module('uLearnHUB', ['MAXClient']);

ulearnhub.controller('DomainsController', ['MAXClient', function (MAXClient) {
    var self = this;
    self.hola = 'que tal';
    self.data = MAXClient.Users;
    self.process = function () {
        console.log("click");
    };
}]);
