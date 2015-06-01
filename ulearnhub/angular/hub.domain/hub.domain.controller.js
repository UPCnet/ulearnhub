(function() {
    'use strict';

    angular
        .module('hub.domain')
        .controller('MainAppController', MainAppController);


    /**
     * @desc
     */
    /* @nInject */
    function MainAppController($stateParams, $cookies, $translate, sidebarSections, hubSession, MAXSession, HUBClientService) {
        var self = this;
        var domainName = hubSession.domain;
        $cookies.currentDomain = $stateParams.domain;
        self.domainObj = HUBClientService.Domain.get({
                id: domainName
            },
            function(response) {},
            function(response) {
                self.error = 'Request to ' + response.config.url + ' failed with code ' + response.status + '.<br/> Server responded: "' + response.data.error_description + '"'

            }
        );
        self.sidebar_status = '';
        self.maxuisettings = {
            generatorName: "uLearn HUB",
            language: "ca",
            oAuthGrantType: "password",
            avatarURLpattern: MAXSession.max_server + "/people/{0}/avatar",
            profileURLpattern: "#",
            username: MAXSession.username,
            oAuthToken: MAXSession.oauth_token,
            maxServerURL: MAXSession.max_server,
            maxServerURLAlias: MAXSession.max_server,
            maxTalkURL: MAXSession.max_server + "/stomp"
        };

        self.toggleSidebar = toggleSidebar;
        self.changeLanguage = changeLanguage;

        ///////////////////////////


        function toggleSidebar(){
            var collapsed = sidebarSections.toggle();
            self.sidebar_status = collapsed ? '' : 'page-sidebar-toggled';
        }

        function changeLanguage(key) {
            $translate.use(key);
        }
    }
})();
