(function() {
    'use strict';

    angular
        .module('hub.sidebar')
        .controller('SidebarController', SidebarController);

    /**
     * @desc
     */
    /* @nInject */
    function SidebarController($state, $stateParams, sidebarSections) {
        var self = this;

        self.sections = sidebarSections.get();
        self.expands = {
            section: undefined,
            subsection: undefined
        };

        self.active = active;
        self.has_sub = has_sub;
        self.expanded = expanded;
        self.expand = expand;

        ////////////////////////

        /**
         * @desc
         */
        function active(section_sref_or_href, sref) {
            var sidebar_url;
            if (sref) {
                sidebar_url = $state.href(section_sref_or_href);
            } else {
                sidebar_url = section_sref_or_href;
            }
            var current_url = $state.href($state.current.name, $stateParams);
            var parent = new RegExp(sidebar_url + '/', "g");
            var is_child = current_url ? current_url.match(parent) !== null : false;
            is_child = is_child && sidebar_url !== '#';
            var is_same = current_url === sidebar_url;
            var is_active = is_child | is_same;
            return is_active ? 'active' : '';
        }

        /**
         * @desc
         */
        function has_sub(subsection) {
            var effective_subsections = subsection === undefined ? [] : subsection;
            return effective_subsections.length > 0 ? 'has-sub' : '';
        }

        /**
         * @desc
         */
        function expanded(section, which) {
            return sidebarSections.expanded(section, which);
        }

        /**
         * @desc
         */
        function expand(section, which) {
            return sidebarSections.expand(section, which);
        }

    }
})();
