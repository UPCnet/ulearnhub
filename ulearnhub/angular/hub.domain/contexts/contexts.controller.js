(function() {
    'use strict';

    angular
        .module('hub.contexts')
        .controller('ContextListController', ContextListController);

    /**
     * @desc
     */
    /* @nInject */
    function ContextListController($cookies, $modal, $log, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, MAXClientService) {
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

        self.application_url = '';
        self.contexts = MAXClientService.Context.query({
            limit: 0
        });


        self.openModal = openModal;
        self.confirmModal = confirmModal;

        //////////////////////////////////////

        /**
         * @desc
         */
        function openModal(size) {

            var modalInstance = $modal.open({
                templateUrl: 'new-context.html',
                controller: 'ModalAddContext',
                size: size,
                resolve: {
                    items: function() {
                        return [];
                    }
                }
            });

            modalInstance.result.then(function(newcontext) {
                self.contexts.push(newcontext);

            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
        }

        /**
         * @desc
         */
        function confirmModal(size, hash) {
            var modalDeleteInstance = $modal.open({
                templateUrl: 'remove-context.html',
                controller: 'ModalDeleteContext',
                size: size,
                resolve: {
                    items: function() {
                        return hash;
                    }
                }
            });

            modalDeleteInstance.result.then(function(newcontext) {
                //aqui va el quitar del listado

            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
        }
    }

})();
