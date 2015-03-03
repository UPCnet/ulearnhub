'use strict';

var ulearnhub = angular.module('uLearnHUB', [
    'hubClient',
    'datatables',
    'datatables.bootstrap',
    'ui.bootstrap'
]);


ulearnhub.controller('DomainsController', ['$modal', '$log', 'Domain', 'DTOptionsBuilder', 'DTColumnDefBuilder', function($modal, $log, Domain, DTOptionsBuilder, DTColumnDefBuilder) {
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

    self.domains = Domain.query();


  self.open = function (size) {

    var modalInstance = $modal.open({
      templateUrl: 'new-domain.html',
      controller: 'ModalInstanceCtrl',
      size: size
    });

    modalInstance.result

    .then(function (newdomain) {
        self.domains.push(newdomain);
        Domain.save(newdomain);
    });
  };


}]);

ulearnhub.controller('ModalInstanceCtrl', function($modalInstance, items) {
  var self = this;

  self.ok = function () {
    $modalInstance.close(self.newdomain);
  };

  self.cancel = function () {
    $modalInstance.dismiss('cancel');
  };
});
