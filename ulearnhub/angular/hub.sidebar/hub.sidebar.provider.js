(function() {
    'use strict';

    angular
        .module('hub.sidebar')
        .provider('sidebarSections', sidebarSectionsProvider);

    /**
     * @desc
     */
    /* @nInject */
    function sidebarSectionsProvider() {
        var sections = [];
        var collapsed = true;
        var expands = {
            section: undefined,
            subsection: undefined
        };

        this.$get = SidebarSections;
        this.setSections = setSections;

        ///////////////////////////

        function setSections(value) {
            sections = value;
        }

        function SidebarSections() {

            var service = {
                toggle: toggle,
                get: get,
                add: add,
                subsection: subsection,
                expanded: expanded,
                expand: expand
            };

            return service;

            /////////////////

            /**
             * @desc
             */
            function toggle() {
                collapsed = !collapsed;
                return collapsed;
            }

            /**
             * @desc
             */
            function get() {
                return sections;
            }

            /**
             * @desc
             */
            function add(newsection) {
                sections.push(newsection);
            }

            /**
             * @desc
             */
            function subsection(section_sref, items) {
                var section = sections.filter(function(el) {
                    return el.sref === section_sref;
                })[0];
                sections[sections.indexOf(section)].subsections = items;
                return section;
            }

            /**
             * @desc
             */
            function expanded(section, which) {
                var value = expands[which] === section;
                return value;
            }

            /**
             * @desc
             */
            function expand(section, which, force) {
                if (expands[which] !== section | force === true) {
                    expands[which] = section;
                } else {
                    expands[which] = undefined;
                }
            }

        }
    }
})();
