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
    });
  };


}]);

ulearnhub.controller('ModalInstanceCtrl', ['$scope', '$modalInstance', 'Domain', function($scope, $modalInstance ,Domain) {
  $scope.alerts = [];

  $scope.ok = function () {
    Domain.save($scope.newdomain)
    .$promise.then(function(data) {
        $modalInstance.close(data);
    }, function(error) {
          $scope.alerts.push({
            type: 'danger',
            msg: error.data.error + ': ' + error.data.error_description});
    });
  };

  $scope.cancel = function () {
    $modalInstance.dismiss('cancel');
  };

  $scope.closeAlert = function(index) {
    $scope.alerts.splice(index, 1);
  };

}]);
