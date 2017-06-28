var app = angular.module("crudApp", []);
app.controller("crud", function($scope, $http){
	$scope.tablesList = [];
	$scope.tableDefinitions={};
	$scope.currentTableRecords = [];	
	$scope.joinFieldMap = {};
	$scope.windows = [];

	$scope.currentTable=null;
	$scope.currentRecord = null;
	$scope.newRecordDefinition = null;

	//do common http failure code
	function httpFailureCallback(error){
		//display an error message
	}

	$scope.editRecord = function(record){
		$scope.currentRecord = record;
		$scope.getTableDefinition($scope.currentTable);
	}

	$scope.deleteRecord = function(record){
		$scope.deleteObject($scope.currentTable,record.id);

	}

	$scope.createNewRecord = function(table) {
		if ($scope.tableDefinitions[table] != null){
			$scope.newRecordDefinition = $scope.tableDefinitions[table];
			return;
		}

		$scope.getTableDefinition(table, function(){
			$scope.newRecordDefinition = $scope.tableDefinitions[table];
		});
	}

	$scope.listRecords = function(table){
		$scope.currentTable = table;
		$scope.getAllRecords(table);
	}

	//get list of tables
	$scope.getTables = function() {
		$http.get("/list_tables").then(function(response){
                	if (!response.data.success){
                        	httpFailureCallback(response.data.message)
	                }
	                $scope.tablesList = response.data.message;
		},
		function(error) {
			httpFailureCallback(error);
		});
	}
	
	//get table definition
	$scope.getTableDefinition = function(tableString, callback) {
		//already have the definition
		if (tableString in $scope.tableDefinitions){
			if (callback) callback();
			return;
		}

		//get new table definition if we don't already have it
		var config = {params:{table:tableString}}
		$http.get("/describe_table", config).then(function(response){
			if (!response.data.success){
				httpFailureCallback(response.data.message);
			}
			$scope.tableDefinitions[tableString] = response.data.message;
			if (callback) callback();

		}, function(error){
			httpFailureCallback(error);
		});
	}

	//persist object
	$scope.persistObject = function(table, objectFields){
		if (objectFields["table"] == null){
			objectFields["table"] = table;
		}
		//object fields must include "table"
		$http.post("/create", objectFields).then(function(response){
			if (!response.data.success){
				httpFailureCallback(response.data.message);
			}
			//some kind of positive action to show saved item	
		}, function(error){
			httpFailureCallback(error);
		});
	}

	//get all objects
	$scope.getAllRecords = function(tableString){
		var config = {params:{table:tableString}};
		$http.get("/list_records", config).then(function(response){
			if (!response.data.success){
				httpFailureCallback(response.data.message);
				return;
			}
			console.log(response.data.message);
			$scope.currentTableRecords = response.data.message;
		}, function(error){
			httpFailureCallback(error);
		});
	}

	//find object
	$scope.getRecord = function(tableString, id){
		var config = {params:{table:tableString, id:id}};
		$http.get("/get_record", config).then(function(response){
			if (!response.data.success){
				httpFailureCallback(response.data.message);
			}
			$scope.currentRecord = data.message;
		}, function(error){
			httpFailureCallback(error);
		});
	}

	//update object
	$scope.updateObject = function(tableString, id, objectFields) {
		if (!("table" in objectFields)){
                        objectFields["table"] = tableString;
                }

		if (!("id" in objectFields)){
			objectFields["id"] = id;
		}

		var config = objectFields;
                $http.post("/update", config).then(function(response){
                        if (!response.data.success){
                                httpFailureCallback(response.data.message);
                        }
                        //update message confirmation
                }, function(error){
                        httpFailureCallback(error);
                });

	}

	//delete object
	$scope.deleteObject = function(tableString, id){
		var config = {table:tableString, id:id};
                $http.post("/delete", config).then(function(response){
                        if (!response.data.success){
                                httpFailureCallback(response.data.message);
                        }
                        //confirmation of delete message
                }, function(error){
                        httpFailureCallback(error);
                });
	}
	

	//lookup join field for table FK
	$scope.getJoinFields = function(tableString, column) {
		if ($scope.joinFieldMap[tableString] != null && $scope.joinFieldMap[tableString][column] != null){
			return;
		}	

		var config = {params:{table:tableString, column:column}};
		$http.get("/table_join_values", function(response){
			if (!response.data.success){
				httpFailureCallback(response.data.message);
			}
			if (!(tableString in $scope.joinFieldMap)){
				$scope.joinFieldMap[tableString] = {};
			}
                        $scope.joinFieldMap[tableString][column] = response.data.message;
			
		}, function(error){
			httpFailureCallback(error);
		});

	}


});
