'use strict';

var ulearnhub = angular.module('uLearnHUB', [
    'hubClient',
    'datatables',
    'datatables.bootstrap'
]);


ulearnhub.controller('DomainsController', ['Domains', 'DTOptionsBuilder', 'DTColumnDefBuilder', function(Domains, DTOptionsBuilder, DTColumnDefBuilder) {
    var self = this;

// Default datatable options
    self.dtOptions = DTOptionsBuilder
        .newOptions().withPaginationType('full_numbers')
        .withBootstrap();

    self.dtColumnDefs = [
        DTColumnDefBuilder.newColumnDef(0),
        DTColumnDefBuilder.newColumnDef(1),
        DTColumnDefBuilder.newColumnDef(2)
    ];

    Domains.query().$promise.then(function(response) {
        self.domains = response;
    });


}]);
