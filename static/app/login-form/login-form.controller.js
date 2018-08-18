angular.module("loginForm").controller("loginFormController", ["$scope", "$http", function($scope, $http){
    var $ctrl = $scope.$ctrl;
    $scope.errorMessage = null;

    $scope.login = function(credentials){
        $scope.errorMessage = null;
        var requiredRequestFields = ["username", "password"]
        if (!$scope.checkRequiredFields(credentials, requiredRequestFields)){
            $scope.loginFailure("Missing required fields.")
            return;
        }

        $http.post("/auth/login", credentials)
        .then(function(response){
            response = response.data;
            var requiredResponseFields = ["username", "session"]
            if (response.success){
                if ($scope.checkRequiredFields(response.message, requiredResponseFields)){
                    $scope.loginSuccess(response.message.username, response.message.session);
                } else {
                    $scope.loginFailure("Malformed response from server.");
                }
            } else {
                $scope.loginFailure(response.message);
            }
        }, function(error){
            $scope.loginFailure(error.statusText)
        });
    };

    $scope.loginSuccess = function(username, session){
        var successData = {"username":username, "session":session}

        if ($ctrl.successCallback){
            $ctrl.successCallback(successData)
        } else {
            $scope.defaultSuccessCallback(successData);
        }
    }

    $scope.loginFailure = function(message){
        var failureData = {"message":message};

        $scope.errorMessage = message;

        if ($ctrl.failureCallback){
            $ctrl.failureCallback(failureData);
        } else {
            $scope.defaultFailureCallback(failureData);
        }
    }

    $scope.setCookie = function(cookieName, cookieValue){
        document.cookie = cookieName+"="+cookieValue+";";
    }

    $scope.defaultFailureCallback = function(errorMessage){
        console.error(errorMessage);
    }

    $scope.defaultSuccessCallback = function(responseMessage){
        console.log(responseMessage);
    }

    $scope.checkRequiredFields = function(messageBody, requiredFields){
        if (messageBody == null || Object.keys(messageBody).length == 0){
            return false;
        }
        for (var i = 0; i < requiredFields.length; i++){
            if (messageBody[requiredFields[i]] == null){
                return false;
            }
        }
        return true;
    }

}]);