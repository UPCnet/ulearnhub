(function() {
    'use strict';

    angular
        .module('hub.domain')
        .factory('EndpointsService', EndpointsService);

    /**
     * @desc
     */
    /* @nInject */
    function EndpointsService($state, $q, sidebarSections, MAXClientService) {
        var endpoints_by_category = {};
        var endpoints = {};

        return {
            loadEndpoints: loadEndpoints,
            getEndpoint: getEndpoint
        };


        function loadEndpoints() {
              var deferred = $q.defer();
              endpoints_by_category = MAXClientService.ApiInfo.by_category();
              endpoints_by_category.$promise.then(function(data) {
                  endpoints_by_category = data;
                  var categories = [];
                  angular.forEach(data, function(category, key) {
                      var subsection = {title: category.name};
                      var thirdlevel = [];
                      angular.forEach(category.resources, function(resource, key) {
                         endpoints[resource.route_id] = resource;
                         endpoints[resource.route_id].category = category.name;
                         var url = $state.href('api.endpoint', {endpoint: resource.route_id});
                         this.push({title: resource.route_name, sref: url});
                      }, thirdlevel);

                      subsection.subsections = thirdlevel;
                      subsection.sref = 'api.' + subsection.title;
                      this.push(subsection);
                  }, categories);

                  sidebarSections.subsection('api', categories);
                  deferred.resolve(data);
              });
              return deferred.promise;
        }

        function getEndpoint(endpoint) {
            return endpoints[endpoint];
        }
    }


})();
