'use strict';

var max_endpoints = angular.module('uLearnHUBDomainManagement');

max_endpoints.controller('ApiController', ['$cookies', 'sidebarSections', 'Endpoints', 'MAXSession', function($cookies, sidebarSections, Endpoints, MAXSession) {
    var self = this;
    self.endpoints_by_cat = Endpoints.query();
    self.info = MAXSession;

    self.endpoints_by_cat.$promise.then(function(data) {
      var categories = [];
      angular.forEach(data, function(category, key) {
          var subsection = {title: category.name};
          var thirdlevel = [];
          angular.forEach(category.resources, function(resource, key) {
             this.push({title: resource.route_name});
          }, thirdlevel);

          subsection.subsections = thirdlevel;
          this.push(subsection);
      }, categories);
      sidebarSections.subsection('api', categories);
    });

}]);
