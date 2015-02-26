'use strict';

var ulearnhub = angular.module('uLearnHUB', ['MAXClient']);

ulearnhub.controller('DomainsController', [function () {
    var self = this;
    self.hola = 'que tal';
    self.process = function () {
        console.log("click");
    };
}]);
