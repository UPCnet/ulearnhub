'use strict';

var max_endpoints = angular.module('uLearnHUBDomainManagement');


max_endpoints.factory('EndpointsService', ['$state', '$q', 'Endpoints', 'sidebarSections', function($state, $q, Endpoints, sidebarSections) {
    var endpoints_by_category = {};
    var endpoints = {};

    return {
      loadEndpoints: function() {
          var deferred = $q.defer();
          endpoints_by_category = Endpoints.query();
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
      },
      getEndpoint: function(endpoint) {
        return endpoints[endpoint];
      }
    };

}]);

max_endpoints.controller('ApiController', ['$cookies', 'sidebarSections', 'MAXSession', function($cookies, sidebarSections, MAXSession) {
    var self = this;
}]);


max_endpoints.controller('EndpointController', ['$http', '$stateParams', '$cookies', 'sidebarSections', 'MAXInfo' ,'EndpointsService', function($http, $stateParams, $cookies, sidebarSections, MAXInfo, EndpointsService) {
    var self = this;
    var route = $stateParams.endpoint;
    var current = EndpointsService.getEndpoint(route);
    var statuses = {
      200: 'Ok',
      400: 'Bad Request'
    };
    self.isActiveMethod = function(method) {
      return method === self.active_method ? 'active': '';
    };

    self.setActiveMethod = function(method) {
      self.active_method = method;
      self.description = current.methods[self.active_method].description;
      self.documentation = current.methods[self.active_method].documentation;
    };

    self.routeParts = function(route_url) {
        var parts = route_url.match(/[^\/]+/g);
        var destination = [];
        _.each(parts, function(element, index, list) {
           if (element[0] === '{') {
            var element_name = element.match(/\{(.*?)\}/)[1];
            // Set separators on 1+ segments
            if (index > 0) {
                // Include / separator at the end of the last segment
                if (_.last(destination).fixed) {
                    _.last(destination).text += '/';
                // Append a fixed / part if last segment was a param
                } else {
                    destination.push({'text': '/', fixed:true, param:false});
                }
            }
            //Add the param element
            destination.push({'text': element, fixed:false, param:true, name:element_name});

           } else {
            var newpart = '/' + element;
            if (index === 0) {
                destination.push({'text': newpart, fixed:true, param:false});
            } else {
                // join together the current ant the last part ig both fixed
                if (_.last(destination).fixed) {
                    _.last(destination).text += newpart;
                // Otherwise add the new fixed part
                } else {
                    destination.push({'text': newpart, fixed:true, param:false});
                }
            }

           }
      });
      return destination;
    };

    self.showError = function(message) {
      self.error.active = true;
      self.error.message = message;
    };

    self.hideError = function() {
      self.error.active = false;
    };

    self.renderResponse = function(data, status, headers, config, finishTime) {
        var json_data = angular.fromJson(data);
        self.response.raw = data;
        self.response.placeholder = '';
        self.response.json = json_data;
        self.response.status = status + ' '+ statuses[status];
        self.response.type = status >= 200 && status < 400 ? 'success' : 'failure';

        var time = finishTime - self.requestStartTime;
        self.response.time = "(" + time + " ms)";

    };

    self.launch = function() {
        self.hideError();
        var url_path = '';
        var missing_or_empty_params = false;
        angular.forEach(self.route, function(route_segment, key) {
            if (route_segment.fixed) {
                url_path += route_segment.text;
            } else {
                var segment_value = self.rest_params[route_segment.name];
                var empty = segment_value === undefined | segment_value === '';
                missing_or_empty_params = missing_or_empty_params && empty;
                url_path += segment_value;
            }
        }, url_path);

        if (missing_or_empty_params) {
          self.showError('Some parameters missing on destination url');
          return;
        }

        var endpoint_url = MAXInfo.max_server + url_path;
        self.requestStartTime =  new Date().getTime();
        $http[self.active_method.toLowerCase()](endpoint_url, {
          headers: MAXInfo.headers,
          transformResponse: function(data, headers) {
            return data;
          }
          }).success(function(data, status, headers, config) {
            var requestFinishTime = new Date().getTime();
            self.renderResponse(data, status, headers, config, requestFinishTime);
          })
          .error(function(data, status, headers, config) {
            var requestFinishTime = new Date().getTime();
            self.renderResponse(data, status, headers, config, requestFinishTime);
          });
    };

    self.methods = [];
    self.available_methods = [];
    angular.forEach(['GET', 'POST', 'PUT', 'DELETE', 'HEAD'], function(method, key) {
       var method_state = {name:method, implemented: current.methods[method] === undefined ? false : true};
       if (current.methods[method] !== undefined) {
          self.available_methods.push(method);
       }
       this.push(method_state);
    }, self.methods);

    self.error = {
      active: false,
      message: 'Error message'
    };

    self.info = MAXInfo.headers;
    self.name = current.route_name;
    self.route = self.routeParts(current.route_url);
    self.rest_params = {};
    self.response = {
      placeholder: 'No response yet, <br/>launch a request first.'
    };
    self.setActiveMethod(self.available_methods[0]);

}]);
