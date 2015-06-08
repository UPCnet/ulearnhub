(function() {
    'use strict';

    angular
        .module('hub')
        .controller('ExceptionsController', ExceptionsController);

    /**
     * @desc
     */
    /* @nInject */
    function ExceptionsController(HUBClientService) {
        var self = this;
        self.exceptions = HUBClientService.Exception.query();

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
