'use strict';

/**
 * @ngdoc function
 * @name sidebar
 * @description
 * # Utilities to manage sidebar links and states
 */


var sidebar = angular.module('sidebar',
    [
        'ui.router'
    ]
);


sidebar.controller('SidebarController', ['$state', '$stateParams', 'sidebarSections', function($state, $stateParams, sidebarSections) {
    var self = this;

    self.sections = sidebarSections.get();
    self.expands = {
      section: undefined,
      subsection: undefined
    };

    self.active = function(section_sref_or_href, sref) {
        var sidebar_url;
        if (sref) {
            sidebar_url = $state.href(section_sref_or_href);
        } else {
            sidebar_url = section_sref_or_href;
        }
        var current_url = $state.href($state.current.name, $stateParams);
        var parent = new RegExp(sidebar_url + '/', "g");
        var is_child = current_url ? current_url.match(parent)!==null: false;
        is_child = is_child && sidebar_url !== '#';
        var is_same = current_url === sidebar_url;
        var is_active = is_child | is_same;
        return is_active ? 'active' : '';
    };

    self.has_sub = function(subsection) {
        var effective_subsections = subsection === undefined ? [] : subsection;
        return effective_subsections.length > 0 ? 'has-sub' : '';
    };

    self.expanded = function(section, which) {
      return sidebarSections.expanded(section, which);
    };


    self.expand = function(section, which) {
      return sidebarSections.expand(section, which);
    };

}]);



sidebar.provider('sidebarSections', function sidebarSectionsProvider() {
  var sections = [];
  var collapsed = true;
  var expands = {
    section: undefined,
    subsection: undefined
  };

  this.setSections = function(value) {
    sections = value;
  };


  this.$get = ['Domain', function(Domain) {
    return {

        toggle: function() {
          collapsed = !collapsed;
          return collapsed;
        },

        get: function() {
          return sections;
        },

        add: function(newsection) {
          sections.push(newsection);
        },
        subsection: function(section_sref, items) {
          var section = sections.filter(function(el) {return el.sref === section_sref;})[0];
          sections[sections.indexOf(section)].subsections = items;
          return section;
        },

        expanded: function(section, which) {
          var value = expands[which] === section;
          return value;
        },

        expand: function(section, which, force) {
          if (expands[which] !== section | force === true) {
            expands[which] = section;
          } else {
            expands[which] = undefined;
          }
        }

    };
  }];
});
