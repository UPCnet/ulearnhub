(function() {
    'use strict';

    angular
        .module('hub')
        .controller('DeploymentDetailController', DeploymentDetailController)
        .controller('NewComponentCtrl', NewComponentCtrl);

    /**
     * @desc
     */
    /* @nInject */
    function DeploymentDetailController($cookies, $filter, $modal, $stateParams, components, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, HUBClientService) {
        var self = this;

        self.obj = HUBClientService.Deployment.get({
            name: $stateParams.name
        });

        self.selectedComponent = {};
        self.components = components;
        self.selectedComponent = self.components[0];

        self.newComponentModal = newComponentModal;
        self.newSubcomponentModal = newSubcomponentModal;
        self.availableSubcomponents = availableSubcomponents;

        /////////////////////////////

        function availableSubcomponents(componentType) {
            return $filter('filter')(self.components, {type:componentType}, true)[0].components;
        }

        function newComponentModal() {
            var modalInstance = $modal.open({
                templateUrl: 'templates/new-component.html',
                controller: 'NewComponentCtrl as newCompCtrl',
                resolve: {
                    component_type: function() {
                        return self.selectedComponent;
                    },
                    deployment_name: function() {
                        return self.obj.name;
                    },
                    parent_component: function() {
                        return undefined;
                    }

                }
            });
            modalInstance.result.then(function() {
                self.obj = HUBClientService.Deployment.get({
                    name: $stateParams.name
                });
            }, function() {

            });

        }

        function newSubcomponentModal(component, subcomponent) {
            var modalInstance = $modal.open({
                templateUrl: 'templates/new-component.html',
                controller: 'NewComponentCtrl as newCompCtrl',
                resolve: {
                    component_type: function() {
                        return subcomponent;
                    },
                    deployment_name: function() {
                        return self.obj.name;
                    },
                    parent_component: function() {
                        return component;
                    }
                }
            });
            modalInstance.result.then(function() {
                self.obj = HUBClientService.Deployment.get({
                    name: $stateParams.name
                });
            }, function() {

            });

        }
    }

    /**
     * @desc
     */
    /* @nInject */
    function NewComponentCtrl($modalInstance, ComponentSchemas, HUBClientService, component_type, deployment_name, parent_component) {
        var self = this;
        self.model = {};
        self.component_type = component_type;
        self.formFields = ComponentSchemas[component_type.type];
        self.onSubmit = onSubmit;
        self.onCancel = onCancel;

        /////////////////////////

        function onSubmit() {
            var name = self.model.name;
            var title = self.model.title;
            delete self.model.name;
            delete self.model.title;

            var new_component = {
                    'component': self.component_type.type,
                    'name': name,
                    'title': title,
                    'params': self.model
                };
            if (parent_component) {
                new_component.parent = parent_component.name;
            }

            HUBClientService.DeploymentComponent.save({
                    name: deployment_name
                }, new_component,
                function(data) {
                    $modalInstance.close(data);
                },
                function() {
                    //fail
                });
        }

        function onCancel() {
            $modalInstance.dismiss('cancel');
        }

    }

})();
