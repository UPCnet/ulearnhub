(function() {
    'use strict';

    angular
        .module('hub')
        .controller('MainAppController', MainAppController);


    /**
     * @desc
     */
    /* @nInject */
    function MainAppController(sidebarSections, $translate) {
        var self = this;
        self.sidebar_status = '';
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
