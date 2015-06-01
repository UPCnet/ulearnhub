(function() {
    'use strict';

    angular
        .module('hub.contexts')
        .controller('ModalAddContext', ModalAddContext)
        .controller('ModalDeleteContext', ModalDeleteContext)
        .controller('ModalUnsubscribeUser', ModalUnsubscribeUser);


    /**
     * @desc
     */
    /* @nInject */
    function ModalAddContext($scope, $modalInstance, MAXClientService) {
        $scope.alerts = [];

        $scope.ok = function() {
            MAXClientService.Context.save($scope.newcontext)
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
    function ModalDeleteContext($scope, $modalInstance, Context, items) {
        $scope.alerts = [];

        var hash = items;
        $scope.ok = function() {
            Context.remove({
                    id: hash
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
    function ModalUnsubscribeUser($scope, $modalInstance, UserSubscribe, items) {
        $scope.alerts = [];

        var username = items[0];
        var hash = items[1];

        $scope.ok = function() {
            UserSubscribe.remove({
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
