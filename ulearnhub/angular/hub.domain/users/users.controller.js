(function() {
    'use strict';

    angular
        .module('hub.users')
        .controller('UserListController', UserListController);

    /**
     * @desc
     */
    /* @nInject */
    function UserListController($cookies, $modal, $log, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, MAXClientService) {
        var self = this;
        var lang = $cookies.currentLang;

        self.search_text = '';

        // Default datatable options

        self.dtOptions = DTOptionsBuilder
            .newOptions().withPaginationType('simple').withDisplayLength(20)
            .withBootstrap()
            .withLanguage(DTTranslations[lang]);

        self.dtColumnDefs = [
            DTColumnDefBuilder.newColumnDef(0),
            DTColumnDefBuilder.newColumnDef(1),
            DTColumnDefBuilder.newColumnDef(2)
        ];

        self.users = [];

        self.search = search;
        self.openModal = openModal;
        self.confirmModal = confirmModal;

        //////////////////////////////////////////////

        /**
         * @desc
         */
        function search() {
            self.users = MAXClientService.User.query({
                username: self.search_text,
                limit: 0
            });
        }

        /**
         * @desc
         */
        function openModal(size) {
            var modalInstance = $modal.open({
                templateUrl: 'new-user.html',
                controller: 'ModalInstanceCtrl',
                size: size,
                resolve: {
                    items: function() {
                        return [];
                    }
                }
            });
            modalInstance.result.then(function(newuser) {
                self.users.push(newuser);
            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
        }

        /**
         * @desc
         */
        function confirmModal(size, username) {
            var modalDeleteInstance = $modal.open({
                templateUrl: 'remove-user.html',
                controller: 'ModalDeleteUser',
                size: size,
                resolve: {
                    items: function() {
                        return username;
                    }
                }
            });
            modalDeleteInstance.result.then(function(username) {
                //aqui va el quitar del listado
                for (var i = 0; i < self.users.length; i += 1) {
                    if (self.users[i].username === username) {
                        self.users.slice(i);
                    }
                }
            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
        }

    }
})();
