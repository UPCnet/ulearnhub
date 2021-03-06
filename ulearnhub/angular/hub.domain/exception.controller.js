/* global Prism */
(function() {
    'use strict';

    angular
        .module('hub.domain')
        .controller('ExceptionController', ExceptionController);

    /**
     * @desc
     */
    /* @nInject */
    function ExceptionController($stateParams, MAXClientService) {
        var self = this;
        self.hash = $stateParams.hash;
        self.exception = MAXClientService.Exception.get({hash: self.hash});
        self.request = '';
        self.exception.$promise.then(function(data) {
          self.request = Prism.highlight(data.request, Prism.languages.http);
          self.traceback = Prism.highlight(data.traceback, Prism.languages.python);
        });
    }

})();
