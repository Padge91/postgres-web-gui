var app = angular.module("crudGuiApp", ["loginForm"]);
app.controller("mainAppController", ["$scope", "$http", function($scope, $http){

    $scope.loginState = "LOGIN";
    $scope.listState = "LIST";
    $scope.selectState = "SELECT";
    $scope.adminState = "ADMIN";

    $scope.currentState = $scope.loginState;

    $scope.changeState = function(state){
        $scope.currentState = state;
    }

    $scope.loginSuccessCallback = function(response){
        $scope.changeState($scope.listState);
    }

    $scope.loginFailureCallback = function(message){
        console.error(message);
    }


}]);