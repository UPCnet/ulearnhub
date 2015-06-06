(function() {
    'use strict';

    angular
        .module('hub')
        .controller('HubUsersController', HubUsersController);

    /**
     * @desc
     */
    /* @nInject */
    function HubUsersController($cookies, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, HUBClientService) {
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
        self.users = HUBClientService.User.query();
        self.domains = HUBClientService.Domain.query();
        self.newuser = {};


        self.changeRole = changeRole;
        self.add = add;
        //////////////////////////////

        /**
         * @desc
         */
        function changeRole(user, role) {
            if (role.active === true) {
                HUBClientService.UserRole.update({
                    role: role.role,
                    domain: user.domain,
                    username: user.username
                }, {});
            } else {
                HUBClientService.UserRole.remove({
                    domain: user.domain,
                    role: role.role,
                    username: user.username
                });
            }
        }

        /**
         * @desc
         */

         function add() {

            HUBClientService.User.save(
                {username:self.newuser.username, domain: self.newuser.domain.name},
                function() {
                //success
                },
                function() {
                //fail
            });
         }

    }
})();
