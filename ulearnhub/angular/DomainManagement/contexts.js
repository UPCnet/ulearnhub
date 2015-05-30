'use strict';

var ulearn_contexts = angular.module('hub.domain');


ulearn_contexts.controller('ContextsManageController', ['$modal', '$log', 'Context','DTOptionsBuilder', 'DTColumnDefBuilder','getUrl','ContextAll','DTTranslations','$cookies', function($modal, $log, Context, DTOptionsBuilder, DTColumnDefBuilder,getUrl,ContextAll,DTTranslations,$cookies) {
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
  self.contexts = ContextAll.query();


// =============== ADD CONTEXT MODAL ================ //

  self.open = function (size) {

    var modalInstance = $modal.open({
      templateUrl: 'new-context.html',
      controller: 'ModalAddContext',
      size: size,
      resolve: {
        items: function () {
          return [];
        }
      }
    });

    modalInstance.result.then(function (newcontext) {
      self.contexts.push(newcontext);

    }, function () {
      $log.info('Modal dismissed at: ' + new Date());
    });
  };


// =============== REMOVE CONTEXT MODAL ================ //

  self.confirmModal = function (size,hash) {
    var modalDeleteInstance = $modal.open({
      templateUrl: 'remove-context.html',
      controller: 'ModalDeleteContext',
      size: size,
      resolve: {
        items: function () {
          return hash;
        }
      }
    });

    modalDeleteInstance.result.then(function (newcontext) {
      //aqui va el quitar del listado

    }, function () {
      $log.info('Modal dismissed at: ' + new Date());
    });
  };

}]);



ulearn_contexts.controller('ContextManageController', ['$scope','$stateParams','$modal', '$log', 'DTTranslations', 'Context','ContextUsers','User','ContextPermissions','DTOptionsBuilder', 'DTColumnDefBuilder','getUrl','UserSubscribeManage','Subscriptions','UserFiltered','$state','$cookies', function($scope,$stateParams,$modal, $log, DTTranslations, Context,ContextUsers, User, ContextPermissions, DTOptionsBuilder, DTColumnDefBuilder,getUrl,UserSubscribeManage,Subscriptions,UserFiltered,$state,$cookies) {

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



    self.contexts = Context.query();

    self.application_url = getUrl;
    self.contextHash = $stateParams.id;

    if(self.newHash){
      self.contextHash = self.newHash;
    }

    Context.get({id:self.contextHash})
    .$promise.then(function(dataContext){
      self.context = dataContext;
      //Get context users Subscribers
      ContextUsers.query({hash:self.context.hash})
      .$promise.then(function(data){
	      var res = ContextPermissions.getToUsersList(data,self.context.hash);
        self.usersList = res[0];
        self.usernameList = res[1];
      });

    });


	self.refreshUsersList = function(search){
	    //Users search to add
		if (search != ''){
			UserFiltered.query({username:search})
			.$promise.then(function(allUsers){
			    	self.usersAvailable = allUsers;

			});
		}
	};

  self.onSelect = function($item,$select){
    for (var i=0; i< $select.selected.length; i++ ){
       if ((self.usernameList.indexOf($select.selected[i].username)) > 0 ){
          $select.removeChoice(i);
       }
    }
  }


  self.changePermission = function(hash,username,permission,state){

    if (state == false){
      UserSubscribeManage.remove({hash:hash,iduser:username,permission:permission});
    }
    else if (state == true){
     UserSubscribeManage.update({hash:hash,iduser:username,permission:permission});
    }

  };


	self.saveContext = function(){
	Context.update({id:self.contextHash},self.context)
	.$promise.then( function(data){
	    var newHash = data.hash;
	  $scope.alerts.push({
	          type: 'success',
	          msg: 'Context successfully saved'});

    $state.go('domain.context',{id:newHash});

	  },function (error){
	  $scope.alerts.push({
	          type: 'danger',
	          msg: error.data.error + ': ' + error.data.error_description});
	});
	};

	$scope.closeAlert = function(index) {
	$scope.alerts.splice(index, 1);
	};


	self.addUsersToContext = function(){
		var users = self.usersSelected;
		var url =  {"objectType": "context","url":self.context.url};
		for (var i=0; i<users. length; i++){
			Subscriptions.save({id:users[i].username,object:url})

		}

    ContextUsers.query({hash:self.context.hash})
    .$promise.then(function(data){
      var res = ContextPermissions.getToUsersList(data,self.context.hash);
      self.usersList = res[0];
      self.usernameList = res[1];
    });

	};



	// =============== REMOVE USER/CONTEXT MODAL ================ //

  self.unsubscribeUser = function (size,username,contextHash) {
    var modalUnsubscribeInstance = $modal.open({
      templateUrl: 'remove-user-context.html',
      controller: 'ModalUnsubscribeUser',
      size: size,
      resolve: {
        items: function () {
          return [username,contextHash];
        }
      }
    });

    modalUnsubscribeInstance.result.then(function (newcontext) {
    	//window.location.reload()
      ContextUsers.query({hash:self.context.hash})
      .$promise.then(function(data){
        var res = ContextPermissions.getToUsersList(data,self.context.hash);
        self.usersList = res[0];
        self.usernameList = res[1];
      });

    }, function () {
      $log.info('Modal dismissed at: ' + new Date());
    });
  };

}]);

ulearn_contexts.controller('ModalAddContext' ,['$scope', '$modalInstance', 'Context' ,function ($scope, $modalInstance, Context) {
$scope.alerts = [];

$scope.ok = function () {
  Context.save($scope.newcontext)
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


ulearn_contexts.controller('ModalDeleteContext' ,['$scope', '$modalInstance', 'Context','items' ,function ($scope, $modalInstance, Context,items) {
$scope.alerts = [];

var hash = items;
$scope.ok = function () {
  Context.remove({id:hash})
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

ulearn_contexts.controller('ModalUnsubscribeUser' ,['$scope', '$modalInstance', 'UserSubscribe','items' ,function ($scope, $modalInstance, UserSubscribe,items) {
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
