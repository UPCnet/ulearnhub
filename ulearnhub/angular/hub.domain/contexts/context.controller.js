(function() {
    'use strict';

    angular
        .module('hub.contexts')
        .controller('ContextDetailsController', ContextDetailsController);

    /**
     * @desc
     */
    /* @nInject */
    function ContextDetailsController($scope, $state, $modal, $cookies, $stateParams, $log, DTOptionsBuilder, DTTranslations, DTColumnDefBuilder, MAXClientService, ContextPermissionsFactory) {
        var self = this;
        $scope.alerts = [];
        self.usersList = [];
        self.usernameList = [];
        self.usersSelected = [];
        self.usersAvailable = [];
        var lang = $cookies.currentLang;
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

        self.contexts = MAXClientService.Context.query();

        self.application_url = '';
        self.contextHash = $stateParams.id;

        if (self.newHash) {
            self.contextHash = self.newHash;
        }

        MAXClientService.Context.get({
                id: self.contextHash
            })
            .$promise.then(function(dataContext) {
                self.context = dataContext;
                //Get context users Subscribers
                MAXClientService.ContextSubscriptions.query({
                        hash: self.context.hash
                    })
                    .$promise.then(function(data) {
                        var res = ContextPermissionsFactory.getToUsersList(data, self.context.hash);
                        self.usersList = res[0];
                        self.usernameList = res[1];
                    });

            });

        self.refreshUsersList = refreshUsersList;
        self.onSelect = onSelect;
        self.changePermission = changePermission;
        self.saveContext = saveContext;
        self.addUsersToContext = addUsersToContext;
        self.unsubscribeUser = unsubscribeUser;

        //////////////////////////////////////

        /**
         * @desc
         */
        function refreshUsersList(search) {
            //Users search to add
            if (search !== '') {
                MAXClientService.User.query({
                        username: search
                    })
                    .$promise.then(function(allUsers) {
                        self.usersAvailable = allUsers;

                    });
            }
        }

        /**
         * @desc
         */
        function onSelect($item, $select) {
            for (var i = 0; i < $select.selected.length; i++) {
                if ((self.usernameList.indexOf($select.selected[i].username)) > 0) {
                    $select.removeChoice(i);
                }
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
                MAXClientService.UserSubscriptionPermission.update({
                    hash: hash,
                    iduser: username,
                    permission: permission
                });
            }

        }

        /**
         * @desc
         */
        function saveContext() {
            MAXClientService.Context.update({
                    id: self.contextHash
                }, self.context)
                .$promise.then(function(data) {
                    var newHash = data.hash;
                    $scope.alerts.push({
                        type: 'success',
                        msg: 'Context successfully saved'
                    });

                    $state.go('context', {
                        id: newHash
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
        $scope.closeAlert = function(index) {
            $scope.alerts.splice(index, 1);
        };

        /**
         * @desc
         */
        function addUsersToContext() {
            var users = self.usersSelected;
            var url = {
                "objectType": "context",
                "url": self.context.url
            };
            for (var i = 0; i < users.length; i++) {
                MAXClientService.UserSubscription.save({
                    id: users[i].username,
                    object: url
                });

            }

            MAXClientService.ContextSubscriptions.query({
                    hash: self.context.hash
                })
                .$promise.then(function(data) {
                    var res = ContextPermissionsFactory.getToUsersList(data, self.context.hash);
                    self.usersList = res[0];
                    self.usernameList = res[1];
                });

        }

        /**
         * @desc
         */
        function unsubscribeUser(size, username, contextHash) {
            var modalUnsubscribeInstance = $modal.open({
                templateUrl: 'remove-user-context.html',
                controller: 'ModalUnsubscribeUser',
                size: size,
                resolve: {
                    items: function() {
                        return [username, contextHash];
                    }
                }
            });

            modalUnsubscribeInstance.result.then(function(newcontext) {
                //window.location.reload()
                MAXClientService.ContextSubscriptions.query({
                        hash: self.context.hash
                    })
                    .$promise.then(function(data) {
                        var res = ContextPermissionsFactory.getToUsersList(data, self.context.hash);
                        self.usersList = res[0];
                        self.usernameList = res[1];
                    });

            }, function() {
                $log.info('Modal dismissed at: ' + new Date());
            });
        }

    }
})();
