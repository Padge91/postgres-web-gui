from flask import Flask, jsonify, request
import queries
import parsing
import dbconn
app = Flask(__name__)



#get table name so we can avoid sql injection
def check_table_name(table):
		fields = {"table":table}
	        #get table name from another table - do this to avoid sql injection
                table_query="select distinct table_name from information_schema.columns where table_name=%(table)s"
                response = dbconn.execute_query(table_query, fields)
                if len(response) < 1 and len(response[0] < 1):
                        raise Exception("Table not found.");
                checked_table=response[0][0]
		return checked_table

#check to make sure we have the fields we need
def check_required_fields(request, required_fields):
	fields = dict()
	if_json = None
	for field in required_fields:
		if field in request.args.keys():
			fields[field] = request.args[field]
		elif field in request.form.keys():
			fields[field] = request.form[field]
		elif request.is_json:
			if if_json is None:
				if_json = request.get_json()

			if field not in if_json.keys():
				raise Exception("Missing required field: " + str(field))

			fields[field] = if_json[field]
		else:
			raise Exception("Missing required field: " + str(field))
	return fields

#get all extra param fields
def get_all_params(request):
	fields = dict()
	for field in request.form:
		fields[field] = request.form[field]
	for field in request.args:
		fields[field] = request.args[field]
	for field in request.get_json():
		fields[field] = request.get_json()[field]
	return fields

#organize a successful response
def organize_success_response(data=None):
	response = {"success":True, "message":data}
	return jsonify(response)
	

#organize failure response
def organize_failure_response(message):
	response = {"success":False, "message":str(message)}
	return jsonify(response)


#index page
@app.route("/", methods=["GET"])
def index():
	return app.send_static_file("html/index.html")


#templates
@app.route("/templates/<file>", methods=["GET"])
def template_file(file):
        return app.send_static_file("templates/"+str(file))


#css files
@app.route("/css/<file>", methods=["GET"])
def css_file(file):
        return app.send_static_file("css/"+str(file))

#fonts files
@app.route("/fonts/<file>", methods=["GET"])
def fonts_file(file):
        return app.send_static_file("fonts/"+str(file))



#js files
@app.route("/js/<file>", methods=["GET"])
def js_file(file):
	return app.send_static_file("js/"+str(file))


#get JSON objects for definitions of tables
@app.route("/list_tables", methods=["GET"])
def list_tables():
	try:
		#connect to database and get tables
		db_response = dbconn.execute_query(queries.table_list_query)
	
		#remove the extra field
		table_list = list()
		for object in db_response:
			if len(object) < 1:
				raise Exception("Query is empty")
			table_list.append(object[0])

		#response
		return organize_success_response(table_list)	
	except Exception as e:
		return organize_failure_response(e)


#list all records for table
@app.route("/list_records", methods=["GET"])
def list_all_records():
	try:
		#check required fields
		required_fields=["table"]
		fields = check_required_fields(request, required_fields)
		
		# I need the table definition so I know which columns are which
		table_def = dbconn.execute_query(queries.table_definition_query, fields)
		full_table_def = parsing.format_all_responses(["name"], table_def)

		#need to order the columns because * can't guarantee column order
		cols = list()
		for item in full_table_def:
			cols.append(item["name"])
		col_order = ",".join(cols)

		checked_table=check_table_name(fields["table"])
	
		#execute query
		query = "select " + col_order + " from " + checked_table
		db_response = dbconn.execute_query(query)
		
		response = list()
		for record in db_response:
			object = dict()
			for i in range(0, len(cols)):
				object[cols[i]] = record[i]
			response.append(object)

		#final response
		return organize_success_response(response)
	except Exception as e:
		return organize_failure_response(e)


#list one record for table
@app.route("/get_record", methods=["GET"])
def list_record():
        try:
                #check required fields
                required_fields=["id", "table"]
                fields = check_required_fields(request, required_fields)

                # I need the table definition so I know which columns are which
                table_def = dbconn.execute_query(queries.table_definition_query, fields)
                full_table_def = parsing.format_all_responses(["name"], table_def)

                #need to order the columns because * can't guarantee column order
                cols = list()
                for item in full_table_def:
                        cols.append(item["name"])
                col_order = ",".join(cols)

		checked_table=check_table_name(fields["table"])

                #execute query
                query = "select " + col_order + " from " + checked_table


                #execute query
                query = "select " + col_order + " from "+checked_table+" where id=%(id)s" 
                db_response = dbconn.execute_query(query, {"table":checked_table,"id":fields["id"]})
                
                response = list()
                for record in db_response:
                        object = dict()
                        for i in range(0, len(cols)):
                                object[cols[i]] = record[i]
                        response.append(object)

                #final response
                return organize_success_response(response)
        except Exception as e:
                return organize_failure_response(e)



#get a table definition with types
@app.route("/describe_table", methods=["GET"])
def get_table_definition():
	try:
		#check required fields
		required_fields = ["table"]
		fields = check_required_fields(request, required_fields)
	
		#execute query
		db_response = dbconn.execute_query(queries.table_definition_query, fields)
	
		#organize the fields
		field_names = ["name", "type", "type"]
		columns = parsing.format_all_responses(field_names, db_response)

		#response
		response = dict()
		response["table"] = fields["table"]
		response["columns"] = columns
		return organize_success_response(response)	
	except Exception as e:
		return organize_failure_response(e)


#persist a new object
@app.route("/create", methods=["POST"])
def persist_object():
	try:
		required_fields = ["table"]
		fields = check_required_fields(request, required_fields)

		#get x params. Do this here because I want all params, not just required ones
		params = get_all_params(request)
		params.pop("table")
	
		#organize the data for insertion
		col_names,format_names = parsing.organize_col_names(params)
	
		checked_table=check_table_name(fields["table"])	

		#insert into database
		query = "insert into "+checked_table+"("+col_names+") values ("+format_names+")"
		dbconn.execute_action_query(query, params)

		#return as json
		return organize_success_response()
	except Exception as e:
		return organize_failure_response(e)


#delete existing object
@app.route("/delete", methods=["POST"])
def delete_object():
	try:
		#get fields
		required_fields = ["id", "table"]
		fields = check_required_fields(request, required_fields)

		checked_table=check_table_name(fields["table"])

		#execute query
		query = "delete from "+checked_table+" where id=%(id)s"
		dbconn.execute_action_query(query, fields)
	
		return organize_success_response()
	except Exception as e:
		return organize_failure_response(e)

#update an existing object
@app.route("/update", methods=["POST"])
def update_object():
	try:
		#get fields
		required_fields = ["id", "table"]
		fields = check_required_fields(request, required_fields)

		#get x params. Do this here because I want all params, not required ones
                params = get_all_params(request)
		params.pop("id", None)
		params.pop("table", None)

		param_string=""
		for key in params:
			param_string+=key+"=%("+key+")s,"
		param_string = param_string[0:len(param_string)-1]
			
		checked_table=check_table_name(fields["table"])

                #build the update query
		query = "update "+checked_table+" set " + param_string + " where id=%(id)s"
		params["id"] = fields["id"]

		#execute query
		dbconn.execute_action_query(query, params)

		#return as json
		return organize_success_response()
	except Exception as e:
		return organize_failure_response(e)


#get a list of values for a multiselect field
@app.route("/table_join_values", methods=["GET"])
def get_join_field_values():
	try:
		required_fields = ["table", "column"]
		fields = check_required_fields(request, required_fields)

		#run query
		db_response = dbconn.execute_query(queries.foreign_keys_query, fields)	
		if len(db_response) < 1:
			raise Exception("Query result is empty.")
	
		#format response
		field_names=["foreign_table", "column", "foreign_column"]
		response = parsing.format_response(field_names, db_response[0])

		#response
		return organize_success_response(response)
	except Exception as e:
		return organize_failure_response(e)

#main method
if __name__=="__main__":
	app.run()

