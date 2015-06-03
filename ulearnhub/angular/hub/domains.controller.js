(function() {
    'use strict';

    angular
        .module('hub')
        .controller('DomainListController', DomainListController)
        .controller('NewDomainModalController', NewDomainModalController);

    /**
     * @desc
     */
    /* @nInject */
    function DomainListController($cookies, $modal, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, HUBClientService) {


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

        self.domains = HUBClientService.Domain.query();


        self.openModal = function(size) {

            var modalInstance = $modal.open({
                templateUrl: 'new-domain.html',
                controller: 'ModalInstanceCtrl',
                size: size
            });

            modalInstance.result
                .then(function(newdomain) {
                    self.domains.push(newdomain);
                });
        };
    }


    /**
     * @desc
     */
    /* @nInject */
    function NewDomainModalController($scope, $modalInstance, HUBClientService) {
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
