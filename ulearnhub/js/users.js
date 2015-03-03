'use strict';

var ulearn_users = angular.module('uLearnUsers', [
    'maxClient',
    'datatables',
    'datatables.bootstrap',
    'ui.bootstrap'
]);

ulearn_users.controller('UsersRolesController', ['$modal', '$log', 'UserRoles','DTOptionsBuilder', 'DTColumnDefBuilder', function($modal, $log, UserRoles, DTOptionsBuilder, DTColumnDefBuilder) {
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
      var usersFinal = [];
     self.users = UserRoles.query()




}]);


ulearn_users.controller('UsersManageController', ['$modal', '$log', 'User','DTOptionsBuilder', 'DTColumnDefBuilder', function($modal, $log, User, DTOptionsBuilder, DTColumnDefBuilder) {
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

     self.users = User.query()


// =============== ADD USER MODAL ================ // 

  self.open = function (size) {

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
      self.users.push(newuser);

    }, function () {
      $log.info('Modal dismissed at: ' + new Date());
    });
  };

}]);


ulearn_users.controller('ModalInstanceCtrl' ,['$scope', '$modalInstance', 'User' ,function ($scope, $modalInstance, User) {
  $scope.alerts = [];

  $scope.ok = function () {
    User.save($scope.newuser)
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