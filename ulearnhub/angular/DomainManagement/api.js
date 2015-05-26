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
      400: 'Bad Request',
      401: 'Unauthorized',
      403: 'Forbidden',
      404: 'Not Found'
    };

    self.isActiveMethod = function(method) {
      return method === self.active_method ? 'active': '';
    };

    self.setActiveMethod = function(method) {
      self.active_method = method;
      self.data = method === 'PUT' | method === 'POST' ? current.methods[self.active_method].payload : undefined;
      self.description = current.methods[self.active_method].description;
      self.documentation = current.methods[self.active_method].documentation;
      var available_method_modifiers = current.methods[self.active_method].modifiers;
      self.has_modifiers = !_.isEmpty(available_method_modifiers);
      self.modifiers_toggle_message = self.has_modifiers ? '(Toggle section to see available modifiers)' : 'No modifiers available';
      angular.forEach(self.modifiers, function(modifier, key) {
          self.modifiers[key].available = _.contains(available_method_modifiers, key);
      });
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

    self.forgeURL = function() {

        // Prepare path part of the url filling in the supplied
        // rest parameters into the route gaps
        var url_path = '';
        var missing_or_empty_params = false;
        angular.forEach(self.route, function(route_segment, key) {
            if (route_segment.fixed) {
                url_path += route_segment.text;
            } else {
                var segment_value = self.rest_params[route_segment.name];
                var empty = segment_value === undefined | segment_value === '';
                missing_or_empty_params = missing_or_empty_params && empty;
                url_path += segment_value === undefined ? '' : segment_value;
            }
        }, url_path);

        // Prepare the query string part of the url using only
        // the enabled ones
        var qs_enabled = {};
        angular.forEach(self.modifiers, function(qs_param, key) {
          if (qs_param.enabled && !_.isEmpty(qs_param.value)) {
            qs_enabled[key] = qs_param.value;
          }
        }, qs_enabled);
        var qs = _.isEmpty(qs_enabled) ? '' : '?' + jQuery.param(qs_enabled);

        // Forge final url combining all parts
        var endpoint_url = MAXInfo.max_server + url_path +  qs;

        self.url = endpoint_url;
        return endpoint_url;
    };

    self.launch = function() {
        self.hideError();
        var missing_or_empty_params = false;
        var endpoint_url = self.forgeURL();

        if (missing_or_empty_params) {
          self.showError('Some parameters missing on destination url');
          return;
        }

        var request = {
          url: endpoint_url,
          method: self.active_method,
          headers: MAXInfo.headers,
          transformResponse: function(data, headers) {
            return data;
          }
        };

        if (self.active_method === 'POST' | self.active_method === 'PUT') {
          request.data = angular.fromJson(self.data);
        }

        self.requestStartTime =  new Date().getTime();
        $http(request)
        .success(function(data, status, headers, config) {
            var requestFinishTime = new Date().getTime();
            self.renderResponse(data, status, headers, config, requestFinishTime);
        })
        .error(function(data, status, headers, config) {
            var requestFinishTime = new Date().getTime();
            self.renderResponse(data, status, headers, config, requestFinishTime);
        });
    };

    self.toggle = function(section) {
      self.visibility[section] = !self.visibility[section];
    };

    // Default values for current endpoint data
    self.name = current.route_name;
    self.route = self.routeParts(current.route_url);
    self.info = MAXInfo.headers;
    self.data = undefined;
    self.response = {
      placeholder: 'No response yet, <br/>launch a request first.'
    };

    // Controls the current and initialstate of the toggable sections
    self.visibility = {
      modifiers: false,
      headers: false,
      documentation: false
    };

    // Default values and state of the elements on Modifiers section

    self.modifiers = {
        limit: {
            enabled:false,
            value:10,
            available:true,
            type: 'text'
        },
        sort: {
            enabled:false,
            value: 'published',
            options: ['published', 'likes', 'flagged'],
            available:true,
            type: 'select'
        },
        priority: {
            enabled:false,
            value: 'activity',
            options: ['activity', 'comments'],
            available:true,
            type: 'select'
        },
        before: {
            enabled:false,
            value:'',
            available:true,
            type: 'text'
        },
        after: {
            enabled:false,
            value:'',
            available:true,
            type: 'text'
        },
        notifications: {
            enabled:false,
            value:0,
            available:true,
            type: 'text'
        }
    };


    // Variable to hold the values for the inputs of the rest variable parts
    self.rest_params = {};

    // Load the methods implemented for the current resource.
    // self.methods will hold the object representing each method
    // self.available methods will hold a list of the implemented ones names
    // This last var is mainly used to determine the method that will be active
    // in the ui by default
    self.methods = [];
    self.available_methods = [];
    angular.forEach(['GET', 'POST', 'PUT', 'DELETE', 'HEAD'], function(method, key) {
       var method_state = {name:method, implemented: current.methods[method] === undefined ? false : true};
       if (current.methods[method] !== undefined) {
          self.available_methods.push(method);
       }
       this.push(method_state);
    }, self.methods);
    self.setActiveMethod(self.available_methods[0]);

    // Object to control display of the endpoint view error message
    self.error = {
      active: false,
      message: 'Error message'
    };

    // Make an initial render of the url with the default parameters
    self.url = self.forgeURL();
}]);
