(function() {
    'use strict';

    angular
        .module('hub')
        .controller('DeploymentListController', DeploymentsListController)
        .controller('NewDeploymentModalController', NewDeploymentModalController);

    /**
     * @desc
     */
    /* @nInject */
    function DeploymentsListController($cookies, $modal, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, HUBClientService) {
        var self = this;
        var lang = $cookies.currentLang;
        // Default datatable options
        self.dtOptions = DTOptionsBuilder
            .newOptions().withPaginationType('full_numbers')
            .withBootstrap()
            .withLanguage(DTTranslations[lang]);

        self.dtColumnDefs = [
            DTColumnDefBuilder.newColumnDef(0),
            DTColumnDefBuilder.newColumnDef(1),
            DTColumnDefBuilder.newColumnDef(2)
        ];

        self.deployments = HUBClientService.Deployment.query();

    }

    /**
     * @desc
     */
    /* @nInject */
    function NewDeploymentModalController($scope, $modalInstance, $modal, HUBClientService) {

        $scope.alerts = [];

        $scope.ok = function() {
            HUBClientService.Domain.save($scope.newdomain)
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
