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

        self.remove = remove;

        /////////////////////

        function remove(exception) {
            HUBClientService.Exception.remove({hash: exception.id}, function () {
                self.exceptions = HUBClientService.Exception.query();
            }, function () {
                //
            });
        }
    }
})();
