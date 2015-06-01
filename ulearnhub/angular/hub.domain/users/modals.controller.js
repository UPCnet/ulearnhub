(function() {
    'use strict';

    angular
        .module('hub.users')
        .controller('ModalInstanceCtrl', ModalInstanceCtrl)
        .controller('ModalDeleteUser', ModalDeleteUser)
        .controller('ModalUnsubscribeContext', ModalUnsubscribeContext);

    /**
     * @desc
     */
    /* @nInject */
    function ModalInstanceCtrl($scope, $modalInstance, MAXClientService, items) {
        $scope.alerts = [];
        $scope.ok = function() {
            MAXClientService.User.save($scope.newuser)
                .$promise.then(function(data) {
                    $modalInstance.close(data);
                }, function(error) {
                    $scope.alerts.push({
                        type: 'danger',
                        msg: error.data.error + ': ' + error.data.error_description
                    });
                });
        };
        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
        };
        $scope.closeAlert = function(index) {
            $scope.alerts.splice(index, 1);
        };
    }


    /**
     * @desc
     */
    /* @nInject */
    function ModalDeleteUser($scope, $modalInstance, MAXClientService, items) {
        $scope.alerts = [];

        var username = items;
        $scope.ok = function() {
            MAXClientService.User.remove({
                    id: username
                })
                .$promise.then(function(data) {
                    $modalInstance.close(data);
                }, function(error) {
                    $scope.alerts.push({
                        type: 'danger',
                        msg: error.data.error + ': ' + error.data.error_description
                    });
                });
        };

        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
        };

        $scope.closeAlert = function(index) {
            $scope.alerts.splice(index, 1);
        };

    }


    /**
     * @desc
     */
    /* @nInject */
    function ModalUnsubscribeContext($scope, $modalInstance, MAXClientService, items) {
        $scope.alerts = [];
        var username = items[0];
        var hash = items[1];
        $scope.ok = function() {
            MAXClientService.UserSubscription.remove({
                    id: username,
                    hash: hash
                })
                .$promise.then(function(data) {
                    $modalInstance.close(data);
                }, function(error) {
                    $scope.alerts.push({
                        type: 'danger',
                        msg: error.data.error + ': ' + error.data.error_description
                    });
                });
        };

        $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
        };

        $scope.closeAlert = function(index) {
            $scope.alerts.splice(index, 1);
        };


    }



})();
