'use strict';

var ulearnhub = angular.module('uLearnHUB', [
    'hubClient',
    'datatables',
    'datatables.bootstrap',
    'ui.bootstrap'
]);


ulearnhub.controller('DomainsController', ['$scope', '$modal', '$log', 'Domains', 'DTOptionsBuilder', 'DTColumnDefBuilder', function($scope, $modal, $log, Domains, DTOptionsBuilder, DTColumnDefBuilder) {
    var self = this;

// Default datatable options
    $scope.dtOptions = DTOptionsBuilder
        .newOptions().withPaginationType('full_numbers')
        .withBootstrap();

    $scope.dtColumnDefs = [
        DTColumnDefBuilder.newColumnDef(0),
        DTColumnDefBuilder.newColumnDef(1),
        DTColumnDefBuilder.newColumnDef(2)
    ];

    Domains.query().$promise.then(function(response) {
        $scope.domains = response;
    });


  $scope.open = function (size) {

    var modalInstance = $modal.open({
      templateUrl: 'new-domain.html',
      controller: 'ModalInstanceCtrl',
      size: size,
      resolve: {
        items: function () {
          return [];
        }
      }
    });

    modalInstance.result.then(function (newdomain) {
        $scope.domains.push(newdomain);
        Domains.save($scope.newdomain);
    }, function () {
      $log.info('Modal dismissed at: ' + new Date());
    });
  };


}]);

ulearnhub.controller('ModalInstanceCtrl', function ($scope, Domains, $modalInstance, items) {

  $scope.ok = function () {
    $modalInstance.close($scope.newdomain);

  };

  $scope.cancel = function () {
    $modalInstance.dismiss('cancel');
  };
});
