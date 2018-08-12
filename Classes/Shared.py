

# check to make sure we have the fields we need
def check_required_fields(request, required_fields):
    fields = {}

    if not request.is_json:
        raise Exception("Request must be of type JSON.")
    json_data = request.get_json()

    for field in required_fields:
        if field not in json_data.keys():
            raise Exception("Missing required field: "+str(field))
        else:
            fields[field] = json_data[field]

    return fields


# error response format
def error_response(message):
    return {"success":False, "message":str(message)}


# error response format
def success_response(message):
    return {"success":True, "message":message}

