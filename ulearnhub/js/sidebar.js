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

    self.sections = sidebarSections

    self.active = function(section) {
        return section == $state.current.name ? 'active' : ''
    };

}]);



sidebar.provider('sidebarSections', function sidebarSectionsProvider() {
  var sections = []

  this.setSections = function(value) {
    sections = value
  };

  this.$get = function() {
    return sections
  }
});
