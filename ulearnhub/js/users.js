'use strict';

var ulearn_users = angular.module('uLearnUsers', [
    'maxClient',
    'datatables',
    'datatables.bootstrap',
    'ui.bootstrap'
]);


ulearn_users.controller('UsersManageController', ['$scope', '$modal', '$log', 'User','DTOptionsBuilder', 'DTColumnDefBuilder', function($scope, $modal, $log, User, DTOptionsBuilder, DTColumnDefBuilder) {
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

/*     var users = User.query(function() {
        console.log(users);
      }); //query() returns all the entries*/

}]);



// =============== ADD USER MODAL ================ // 

ulearn_users.controller('ModalAddUser',['$scope','$modal','$log', 'User',function ($scope,$modal,$log, User) {
  $scope.open = function (size) {

    var modalInstance = $modal.open({
      templateUrl: 'new-user.html',
      controller: 'ModalInstanceCtrl',
      size: size,
      resolve: {
        items: function () {
          return [];
        }
      }
    });

    modalInstance.result.then(function (newuser) {
      $scope.user.push(newuser);
      debugger
      /*Domains.save($scope.newuser);*/
    }, function () {
      $log.info('Modal dismissed at: ' + new Date());
    });
  };

}]);


ulearn_users.controller('ModalInstanceCtrl', function ($scope, User, $modalInstance, items) {

  $scope.ok = function () {
    $modalInstance.close($scope.newuser);

  };

  $scope.cancel = function () {
    $modalInstance.dismiss('cancel');
  };
});