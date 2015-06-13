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
    function DeploymentDetailController($cookies, $modal, $stateParams, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, HUBClientService) {
        var self = this;

        self.obj = HUBClientService.Deployment.get({
            name: $stateParams.name
        });

        self.newComponentModal = newComponentModal;
        self.selectedComponent = {};
        self.components = HUBClientService.Component.query();

        self.components.$promise.then(function(data) {
            self.selectedComponent = data[0];
        });

        /////////////////////////////

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
                    }
                }
            });
            modalInstance.result.then(function(newuser) {
                self.users.push(newuser);
            }, function() {

            });

        }
    }

    /**
     * @desc
     */
    /* @nInject */
    function NewComponentCtrl($modalInstance, ComponentSchemas, HUBClientService, component_type, deployment_name) {
        var self = this;

        self.model = {};
        self.component_type = component_type;
        self.formFields = ComponentSchemas[component_type.name];
        self.onSubmit = onSubmit;
        self.onCancel = onCancel;

        /////////////////////////

        function onSubmit() {
            var name = self.model.name;
            var title = self.model.title;
            delete self.model.name;
            delete self.model.title;
            HUBClientService.DeploymentComponent.save({
                    name: deployment_name
                }, {
                    'component': self.component_type.name,
                    'name': name,
                    'title': title,
                    'params': self.model
                },
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
