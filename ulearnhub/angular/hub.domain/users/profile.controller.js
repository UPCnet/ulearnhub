(function() {
    'use strict';

    angular
        .module('hub.users')
        .controller('UserProfileController', UserManageController);

    /**
     * @desc
     */
    /* @nInject */
    function UserManageController($cookies, $scope, $stateParams, $modal, $log, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, MAXClientService, ContextPermissionsFactory) {

        var self = this;
        var lang = $cookies.currentLang;
        $scope.alerts = [];
        // Default datatable options
        self.dtOptions = DTOptionsBuilder
            .newOptions().withPaginationType('full_numbers')
            .withBootstrap()
            .withLanguage(DTTranslations[lang]);
        self.dtColumnDefs = [
            DTColumnDefBuilder.newColumnDef(0),
            DTColumnDefBuilder.newColumnDef(1),
            DTColumnDefBuilder.newColumnDef(2)
        ];
        self.username = $stateParams.id;
        self.contextAvailable = MAXClientService.Context.query();
        MAXClientService.User.getUsu({
                id: self.username
            })
            .$promise.then(function(data) {
                self.user = data;
                var res = ContextPermissionsFactory.getToContextList(data);
                self.contextsList = res[0];
                self.urlList = res[1];
                self.user.large_avatar = 'http://localhost:8081/people/' + self.user.username + '/avatar/large';
            });

        self.refreshContextList = refreshContextList;
        self.changePermission = changePermission;
        self.saveUser = saveUser;
        self.closeAlert = closeAlert;
        self.addContextToUser = addContextToUser;
        self.unsubscribeContext = unsubscribeContext;

        //////////////////////////////////

        /**
         * @desc
         */
        function refreshContextList(search) {
            //Users search to add
            if (search !== '') {
                MAXClientService.User.query({
                        username: search
                    })
                    .$promise.then(function(data) {
                        self.contextAvailable = data;
                    });
            }
        }

        /**
         * @desc
         */
        function changePermission(hash, username, permission, state) {
            if (state === false) {
                MAXClientService.UserSubscriptionPermission.remove({
                    hash: hash,
                    iduser: username,
                    permission: permission
                });
            } else if (state === true) {
                MAXClientService.MAXClientService.UserSubscriptionPermission.update({
                    hash: hash,
                    iduser: username,
                    permission: permission
                });
            }
        }

        /**
         * @desc
         */
        function saveUser() {
            MAXClientService.User.update({
                    id: self.username
                }, self.user)
                .$promise.then(function(data) {
                    $scope.alerts.push({
                        type: 'success',
                        msg: 'User successfully saved'
                    });
                }, function(error) {
                    $scope.alerts.push({
                        type: 'danger',
                        msg: error.data.error + ': ' + error.data.error_description
                    });
                });
        }

        /**
         * @desc
         */
        function closeAlert(index) {
            $scope.alerts.splice(index, 1);
        }

        /**
         * @desc
         */
        function addContextToUser() {
            var contexts = self.contextsSelected;
            var username = self.username;
            for (var i = 0; i < contexts.length; i++) {
                var url = {
                    "objectType": "context",
                    "url": contexts[i].url
                };
                MAXClientService.UserSubscription.save({
                    id: username,
                    object: url
                });
            }
            MAXClientService.User.getUsu({
                    id: self.username
                })
                .$promise.then(function(data) {
                    self.user = data;
                    var res = ContextPermissionsFactory.getToContextList(data);
                    self.contextsList = res[0];
                    self.urlList = res[1];
                });
        }

        /**
         * @desc
         */
        function unsubscribeContext(size, username, contextHash) {
            var modalUnsubscribeInstance = $modal.open({
                templateUrl: 'unsubscribe-context.html',
                controller: 'ModalUnsubscribeContext',
                size: size,
                resolve: {
                    items: function() {
                        return [username, contextHash];
                    }
                }
            });
            modalUnsubscribeInstance.result.then(function(newcontext) {
                //aqui va el quitar del listado
                MAXClientService.User.getUsu({
                        id: self.username
                    })
                    .$promise.then(function(data) {
                        self.user = data;
                        var res = ContextPermissionsFactory.getToContextList(data);
                        self.contextsList = res[0];
                        self.urlList = res[1];
                    });
            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
        }
    }
})();
