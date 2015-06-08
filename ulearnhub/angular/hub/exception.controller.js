/* global Prism */
(function() {
    'use strict';

    angular
        .module('hub')
        .controller('ExceptionController', ExceptionController);

    /**
     * @desc
     */
    /* @nInject */
    function ExceptionController($stateParams, HUBClientService) {
        var self = this;
        self.hash = $stateParams.hash;
        self.exception = HUBClientService.Exception.get({hash: self.hash});
        self.request = '';
        self.exception.$promise.then(function(data) {
          self.request = Prism.highlight(data.request, Prism.languages.http);
          self.traceback = Prism.highlight(data.traceback, Prism.languages.python);
        });
    }

})();
