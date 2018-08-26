var app = angular.module("crudGuiApp", ["loginForm", "drilldownList", "ribbon", "recordList"]);
app.controller("mainAppController", ["$scope", "$http", function($scope, $http){

    $scope.loginState = "LOGIN";
    $scope.listState = "LIST";
    $scope.selectState = "SELECT";
    $scope.adminState = "ADMIN";

    $scope.currentState = $scope.loginState;

    // variables to store data
    $scope.tables = [];
    $scope.tableDefinitions = {};
    $scope.currentTable = null;
    $scope.currentTableRecords = null;

    // simple history management (not state, just pages)
    $scope.simpleHistory = [$scope.currentState];
    $scope.historyIndex = 0;

    $scope.changeState = function(state){
        $scope.currentState = state;
        $scope.simpleHistory.push(state);
        $scope.historyIndex = $scope.simpleHistory.length-1;
    }

    $scope.reverseState = function(){
        $scope.historyIndex = $scope.simpleHistory.length-2
        $scope.simpleHistory.remove($scope.simpleHistory.length-1)
    }

    $scope.loginSuccessCallback = function(response){
        $scope.getTables(function(data){
            $scope.tables = data;
            $scope.changeState($scope.listState);
        },
        function(error){
            console.error(error);
            $scope.changeState($scope.listState);
        })
    }

    $scope.loginFailureCallback = function(message){
        console.error(message);
    }

    $scope.selectCallback = function(selectedItem){
        $scope.getTableDefinition(selectedItem, function(tableDefinition){
            $scope.tableDefinitions[selectedItem] = tableDefinition;
            $scope.currentTable = selectedItem;
            $scope.getAllRecords(selectedItem,
            function(data){
                $scope.currentTableRecords = data;
                $scope.changeState($scope.selectState);
            },
            function(error){
                console.error(error)
            })
        }, function(error){
            console.error(error)
        });
    }

    //get list of tables
	$scope.getTables = function(successCallback, failureCallback) {
		$http.get("/list_tables")
		.then(function(response){
                	if (!response.data.success){
                        	failureCallback(response.data.message);
	                }
	                successCallback(response.data.message);
		},
		function(error) {
			failureCallback(response.data.message);
		});
	}

	//get table definition
	$scope.getTableDefinition = function(tableName, successCallback, failureCallback) {
		//already have the definition
		if (tableName in $scope.tableDefinitions){
			successCallback($scope.tableDefinitions[tableName]);
		}
		//get new table definition if we don't already have it
		var config = {params:{table:tableName}}
		$http.get("/describe_table", config)
		.then(function(response){
			if (!response.data.success){
				FailureCallback(response.data.message);
			}
			// caching results
			$scope.tableDefinitions[tableName] = response.data.message;
			successCallback(response.data.message);
		}, function(error){
			failureCallback(error);
		});
	}

	//get all objects
	$scope.getAllRecords = function(tableName, successCallback, failureCallback){
		var config = {params:{table:tableName}};
		$http.get("/list_records", config)
		.then(function(response){
			if (!response.data.success){
				failureCallback(response.data.message);
			}
			successCallback(response.data.message);
		}, function(error){
			failureCallback(error);
		});
	}


}]);