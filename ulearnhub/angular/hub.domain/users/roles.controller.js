(function() {
    'use strict';

    angular
        .module('hub.users')
        .controller('UsersRolesController', UsersRolesController);

    /**
     * @desc
     */
    /* @nInject */
    function UsersRolesController($cookies, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, MAXClientService) {
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
        self.users = MAXClientService.SecurityUsers.query();

        self.changeRole = changeRole;

        //////////////////////////////

        /**
         * @desc
         */
        function changeRole(state, rolename, username) {
            if (state === true) {
                MAXClientService.SecurityUserRole.save({
                    idrol: rolename,
                    iduser: username
                });
            }
            if (state === false) {
                MAXClientService.SecurityUserRole.remove({
                    idrol: rolename,
                    iduser: username
                });
            }
        }
    }

})();
