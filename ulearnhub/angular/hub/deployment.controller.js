(function() {
    'use strict';

    angular
        .module('hub')
        .controller('DeploymentDetailController', DeploymentDetailController);

    /**
     * @desc
     */
    /* @nInject */
    function DeploymentDetailController($cookies, $stateParams, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, HUBClientService) {
        var self = this;

        self.obj = HUBClientService.Deployment.get({name: $stateParams.name});
    }


})();
