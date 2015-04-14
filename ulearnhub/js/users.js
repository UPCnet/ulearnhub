'use strict';

var ulearn_users = angular.module('uLearnHUB');

ulearn_users.controller('UsersRolesController', ['$modal', '$log','$scope', 'UsersRoles','UserRoleManage','DTOptionsBuilder', 'DTColumnDefBuilder','$cookies','DTTranslations', function($modal, $log, $scope, UsersRoles, UserRoleManage, DTOptionsBuilder, DTColumnDefBuilder,$cookies,DTTranslations) {
  var self = this;
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
    var usersFinal = [];
   self.users = UsersRoles.query();


  // Update roles user.
  self.changeRole = function(state, rolename, username) {
      if (state == true) {
        UserRoleManage.save({idrol:rolename,iduser:username});
      }
      if (state == false){
       UserRoleManage.remove({idrol:rolename,iduser:username});
     }

   };

}]);


ulearn_users.controller('UserManageController', ['$scope','$stateParams','$modal', '$log','getUrl','ContextPermissions', 'User','UserSubscribeManage','DTOptionsBuilder', 'DTColumnDefBuilder','Context','Subscriptions','$cookies','DTTranslations', function($scope,$stateParams,$modal, $log, getUrl,ContextPermissions, User,UserSubscribeManage, DTOptionsBuilder, DTColumnDefBuilder,Context,Subscriptions,$cookies,DTTranslations) {
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

  self.application_url = getUrl;
  self.username = $stateParams.id;

  self.contextAvailable = Context.query();

  User.getUsu({id:self.username})
  .$promise.then(function(data) {
    self.user = data;
    var res = ContextPermissions.getToContextList(data);
    self.contextsList = res[0];
    self.urlList = res[1];

  });


  self.refreshContextList = function(search){
      //Users search to add
    if (search != ''){
      UserFiltered.query({username:search})
      .$promise.then(function(data){
            self.contextAvailable = data;

      });
    }
  };

  self.changePermission = function(hash,username,permission,state){

    if (state == false){
      UserSubscribeManage.remove({hash:hash,iduser:username,permission:permission});
    }
    else if (state == true){
     UserSubscribeManage.update({hash:hash,iduser:username,permission:permission});
    }

  };

  $scope.saveUser = function (){
    User.update({id:self.username},self.user)
    .$promise.then(function(data){

    $scope.alerts.push({
                type: 'success',
                msg: 'User successfully saved'});

    },function (error){
    $scope.alerts.push({
            type: 'danger',
            msg: error.data.error + ': ' + error.data.error_description});
    });
  };

  $scope.closeAlert = function(index) {
    $scope.alerts.splice(index, 1);
  };


	self.addContextToUser = function(){
		var contexts = self.contextsSelected;
		var username = self.username;
		for (var i=0; i<contexts.length; i++){
			var url =  {"objectType": "context","url":contexts[i].url};
			Subscriptions.save({id:username,object:url})

		}
		  User.getUsu({id:self.username})
      .$promise.then(function(data) {
        self.user = data;
        var res = ContextPermissions.getToContextList(data);
        self.contextsList = res[0];
        self.urlList = res[1];
      });
	};

	// =============== UNSUBSCRIBE USER/CONTEXT MODAL ================ //

  self.unsubscribeContext = function (size,username,contextHash) {
    var modalUnsubscribeInstance = $modal.open({
      templateUrl: 'unsubscribe-context.html',
      controller: 'ModalUnsubscribeContext',
      size: size,
      resolve: {
        items: function () {
          return [username,contextHash];
        }
      }
    });

    modalUnsubscribeInstance.result.then(function (newcontext) {
      //aqui va el quitar del listado
      User.getUsu({id:self.username})
      .$promise.then(function(data) {
        self.user = data;
        var res = ContextPermissions.getToContextList(data);
        self.contextsList = res[0];
        self.urlList = res[1];
      });

    }, function () {
      $log.info('Modal dismissed at: ' + new Date());
    });
  };




}]);


ulearn_users.controller('UsersManageController', ['$modal','getUrl', '$log', 'User','DTOptionsBuilder', 'DTColumnDefBuilder','UserAll','$cookies','DTTranslations', function($modal,getUrl, $log, User, DTOptionsBuilder, DTColumnDefBuilder,UserAll,$cookies,DTTranslations) {
    var self = this;
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

    self.application_url = getUrl;
    self.users = UserAll.query();


// =============== ADD USER MODAL ================ // 

  self.open = function (size) {

    var modalInstance = $modal.open({
      templateUrl: 'new-user.html',
      controller: 'ModalInstanceCtrl',
      size: size,
      resolve: {
        items: function () {
          return [];
        }
      }
    });

    modalInstance.result.then(function (newuser) {
      self.users.push(newuser);

    }, function () {
      $log.info('Modal dismissed at: ' + new Date());
    });
  };


// =============== REMOVE USER MODAL ================ //

  self.confirmModal = function (size,username) {
    var modalDeleteInstance = $modal.open({
      templateUrl: 'remove-user.html',
      controller: 'ModalDeleteUser',
      size: size,
      resolve: {
        items: function () {
          return username;
        }
      }
    });

    modalDeleteInstance.result.then(function (username) {
      //aqui va el quitar del listado
      for(var i = 0 ; i < self.users.length; i += 1) {
        if (self.users[i].username == username) {self.users.slice(i);}
      }

    }, function () {
      $log.info('Modal dismissed at: ' + new Date());
    });
  };

}]);


ulearn_users.controller('ModalInstanceCtrl' ,['$scope', '$modalInstance', 'User' ,function ($scope, $modalInstance, User) {
  $scope.alerts = [];

  $scope.ok = function () {
    User.save($scope.newuser)
   .$promise.then(function(data) {
        $modalInstance.close(data);
    }, function(error) {
          $scope.alerts.push({
            type: 'danger',
            msg: error.data.error + ': ' + error.data.error_description});
    });
  };

  $scope.cancel = function () {
    $modalInstance.dismiss('cancel');
  };

  $scope.closeAlert = function(index) {
    $scope.alerts.splice(index, 1);
  };

}]);



ulearn_users.controller('ModalDeleteUser' ,['$scope', '$modalInstance', 'User','items' ,function ($scope, $modalInstance, User,items) {
$scope.alerts = [];

var username = items;
$scope.ok = function () {
  User.remove({id:username})
 .$promise.then(function(data) {
      $modalInstance.close(data);
  }, function(error) {
        $scope.alerts.push({
          type: 'danger',
          msg: error.data.error + ': ' + error.data.error_description});
  });
};

$scope.cancel = function () {
  $modalInstance.dismiss('cancel');
};

$scope.closeAlert = function(index) {
  $scope.alerts.splice(index, 1);
};

}]);


ulearn_users.controller('ModalUnsubscribeContext' ,['$scope', '$modalInstance', 'UserSubscribe','items' ,function ($scope, $modalInstance, UserSubscribe,items) {
$scope.alerts = [];
var username = items[0];
var hash = items[1];
$scope.ok = function () {
  UserSubscribe.remove({id:username,hash:hash})
 .$promise.then(function(data) {
      $modalInstance.close(data);
  }, function(error) {
        $scope.alerts.push({
          type: 'danger',
          msg: error.data.error + ': ' + error.data.error_description});
  });
};

$scope.cancel = function () {
  $modalInstance.dismiss('cancel');
};

$scope.closeAlert = function(index) {
  $scope.alerts.splice(index, 1);
};

}]);
