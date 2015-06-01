(function() {
    'use strict';

    angular
        .module('hub.contexts')
        .factory('ContextPermissionsFactory', ContextPermissionsFactory);

    /**
     * @desc
     */
    /* @nInject */
    function ContextPermissionsFactory() {
        return {
            getToContextList: getToContextList,
            getToUsersList: getToUsersList
        };

        //////////////////

        /**
         * @desc
         */
        function getToContextList(userObj) {
            var read = false;
            var write = false;
            var delet = false;
            var unsubscribe = false;
            var stringPermis = [];
            var contextsList = [];
            var urlList = [];

            if (userObj.subscribedTo) {
                for (var i = 0; i < userObj.subscribedTo.length; i++) {

                    for (var j = 0; j < userObj.subscribedTo[i].permissions.length; j++) {
                        stringPermis = userObj.subscribedTo[i].permissions[j];
                        if (stringPermis === 'read') {
                            read = true;
                        } else if (stringPermis === 'write') {
                            write = true;
                        } else if (stringPermis === 'unsubscribe') {
                            unsubscribe = true;
                        } else if (stringPermis === 'delete') {
                            delet = true;
                        }
                    }

                    contextsList.push({
                        displayName: userObj.subscribedTo[i].displayName,
                        url: userObj.subscribedTo[i].url,
                        hash: userObj.subscribedTo[i].hash,
                        permissionRead: read,
                        permissionWrite: write,
                        permissionUnsubscribe: unsubscribe,
                        permissionDelete: delet
                    });
                    urlList.push(userObj.subscribedTo[i].url);
                }

            }
        return [contextsList, urlList];
        }

        /**
        * @desc
        */
        function getToUsersList(userObj, contextHash) {

            var resuList = [];
            var usernameList = [];
            for (var i = 0; i < userObj.length; i++) {
                var read = false;
                var write = false;
                var delet = false;
                var unsubscribe = false;
                var stringPermis = [];


                for (var j = 0; j < userObj[i].permissions.length; j++) {
                    stringPermis = userObj[i].permissions[j];
                    if (stringPermis === 'read') {
                        read = true;
                    } else if (stringPermis === 'write') {
                        write = true;
                    } else if (stringPermis === 'unsubscribe') {
                        unsubscribe = true;
                    } else if (stringPermis === 'delete') {
                        delet = true;
                    }
                }
                resuList.push({
                    username: userObj[i].username,
                    permissionRead: read,
                    permissionWrite: write,
                    permissionUnsubscribe: unsubscribe,
                    permissionDelete: delet,
                    hash: contextHash
                });
                usernameList.push(userObj[i].username);
            }
            return [resuList, usernameList];
        }
    }
})();
