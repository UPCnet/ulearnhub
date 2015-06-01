(function() {
    'use strict';

    angular
        .module('hub.domain')
        .controller('ExceptionsController', ExceptionsController);

    /**
     * @desc
     */
    /* @nInject */
    function ExceptionsController(MAXClientService) {
        var self = this;
        self.exceptions = MAXClientService.Exception.query();
    }
})();
