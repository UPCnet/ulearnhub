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


sidebar.controller('SidebarController', ['$state', 'sidebarSections', function($state, sidebarSections) {
    var self = this;

    self.sections = sidebarSections.get();
    self.expands = {
      section: undefined,
      subsection: undefined
    };

    self.active = function(section_sref) {
        return section_sref === $state.current.name ? 'active' : '';
    };

    self.has_sub = function(subsection) {
        var effective_subsections = subsection === undefined ? [] : subsection;
        return effective_subsections.length > 0 ? 'has-sub' : '';
    };

    self.expanded = function(section, which) {
      return self.expands[which] === section;
    };


    self.expand = function(section, which) {
      if (self.expands[which] === section) {
        self.expands[which] = undefined;
      } else {
        self.expands[which] = section;
      }
    };

}]);



sidebar.provider('sidebarSections', function sidebarSectionsProvider() {
  var sections = [];

  this.setSections = function(value) {
    sections = value;
  };


  this.$get = ['Domain', function(Domain) {
    return {
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
        }

    };
  }];
});
