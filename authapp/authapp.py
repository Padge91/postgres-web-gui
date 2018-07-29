from flask import Flask, jsonify, request
import bcrypt
import dbconn
import parsing

import uuid

app = Flask(__name__)

# Web server to handle authentication. Doing this in HTTP so we can use SSL for security purposes, rather than UDP
password_min_length = 12;
sessions = []


# check to make sure we have the fields we need
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


# get all extra param fields
def get_all_params(request):
    fields = dict()
    for field in request.form:
        fields[field] = request.form[field]
    for field in request.args:
        fields[field] = request.args[field]
    for field in request.get_json():
        fields[field] = request.get_json()[field]
    return fields


# organize a successful response
def organize_success_response(data=None):
    response = {"success": True, "message": data}
    return jsonify(response)


# organize failure response
def organize_failure_response(message):
    response = {"success": False, "message": str(message)}
    return jsonify(response)


# check if password meets minimum requirements
def validate_password(pw):
    if len(pw) < password_min_length:
        raise Exception("Password must be at least " + str(password_min_length) + " characters.")

    if any(x.isupper() for x in pw) and any(x.islower() for x in s) and any(x.isdigit() for x in s):
        raise Exception("Password must contain at least one capital letter, one lowercase letter, and a number")


def generate_session_id():
    return uuid.uuid4()


def get_id_from_session(session):
    for object in sessions:
        if object["session"] == session:
            return object["id"]
    return None


def remove_session(session):
    for i in range(0, len(sessions)):
        if sessions[i]["session"] == session:
            sessions.pop(i);


# get characters list from account
@app.route("/list_characters", methods=["GET"])
def list_characters():
    try:
        required_fields = ["session"]
        fields = check_required_fields(request, required_fields)

        account_id = get_id_from_session(fields["session"])
        if account_id is None:
            raise Exception("No session found.")
        results = dbconn.execute_query(
            "select player_characters.id, player_characters.name, player_characters.race_id, player_characters.class_id, player_characters.race_model_id from player_characters where player_characters.id in (select character_id from account_characters where account_id=%(id)s)",
            {"id": account_id})

        real_results = parsing.format_all_responses(["id", "name", "race_id", "class_id", "race_model_id"], results)

        return organize_success_response(real_results)
    except Exception as e:
        return organize_failure_response(e)


# create character
@app.route("/create_character", methods=["POST"])
def create_character():
    try:
        required_fields = ["session", "name", "race_id", "model_id", "gender_id"]
        fields = check_required_fields(request, required_fields)

        account_id = get_id_from_session(fields["session"])
        if account_id is None:
            raise Exception("No session found.")
        fields["id"] = account_id

        id_of_inserted = dbconn.execute_action_query(
            "insert into player_characters (name, race_id, class_id, race_model_id, gender_id) values (%(name)s, %(race_id)s, NULL, %(model_id)s, %(gender_id)s) returning id",
            fields)
        dbconn.execute_action_query(
            "insert into account_characters(account_id, character_id) values (%(account_id)s, %(character_id)s)",
            {"account_id": account_id, "character_id": id_of_inserted})

        return organize_success_response()
    except Exception as e:
        return organize_failure_response(e)


# account creation
@app.route("/create_account", methods=["POST"])
def create_account():
    try:
        required_fields = ["username", "email", "password", "passwordConfirm"]
        fields = check_required_fields(request, required_fields)

        if fields["password"] != fields["passwordConfirm"]:
            raise Exception("Passwords do not match")

        validate_password(fields["password"])

        # check to see if an account with username exists
        results = dbconn.execute_query("select username from accounts where username=%(username)s",
                                       {"username": fields["username"]})
        if len(results) > 0:
            raise Exception("Username is already in use.")

        # check to see if an account with email exists
        results = dbconn.execute_query("select username from accounts where email=%(email)s",
                                       {"email": fields["email"]})
        if len(results) > 0:
            raise Exception("Email is already in use.")

        # hash password and save
        salt = bcrypt.gensalt()
        pw_hash = bcrypt.hashpw(fields["password"].encode("utf-8"), salt)

        # insert
        fields["salt"] = salt
        fields["password"] = pw_hash
        dbconn.execute_action_query(
            "insert into accounts(username, email, password, salt, account_creation) values(%(username)s, %(email)s, %(password)s,%(salt)s,now())",
            fields)

        return organize_success_response()
    except Exception as e:
        return organize_failure_response(e)


# forgotten password reset
@app.route("/reset_password", methods=["POST"])
def reset_password():
    try:
        required_fields = ["username"]

        # send email with a link to url with an argument specific for a user. The url will then go to a specific endpoint

        return organize_success_response()
    except Exception as e:
        return organize_failure_response(e)


# login to character
@app.route("/character_login", methods=["POST"])
def character_login():
    try:
        # get character info, like location and such
        required_fields = ["session", "character_id"]
        fields = check_required_fields(request, required_fields)

        # get account id
        account_id = get_id_from_session(fields["session"])
        if account_id is None:
            raise Exception("No session found.")
        fields["account_id"] = account_id

        # verify character id
        char_results = dbconn.execute_query(
            "select account_id, character_id from account_characters where account_id=%(account_id)s and character_id=%(character_id)s",
            fields)
        if len(char_results) == 0:
            raise Exception("No character found.")

        character_id = char_results[0][1]
        character_session = generate_session_id()

        existing_query = "select * from character_sessions where character_id=%(id)s"
        c = dbconn.execute_query(existing_query, {"id":character_id})
        query2 = ""
        if len(c) > 0:
            query2 = "update character_sessions set character_session=%(character_session)s, session_expire=now()+'1 hour' where character_id=%(character_id)s"
        else:
            query2 = "insert into character_sessions (character_id, character_session, session_expire) values (%(character_id)s, %(character_session)s, now() + '1 hour')"
        
        new_fields = {"character_id":character_id, "character_session":str(character_session)}
        dbconn.execute_action_query(query2, new_fields)

        # need things the player needs to know about their player
        # really everything related to the character
        # character position and rotation, items, spells, currency, professions, equipment, quest availability
        character_definition = {"session":str(character_session)}

        location_and_rotation = dbconn.execute_query("select position_x, position_y, position_z, quaternion_x, quaternion_y, quaternion_z, quaternion_w from player_characters where id=%(character_id)s", fields)
        resp = parsing.format_all_responses(["position_x", "position_y", "position_z", "quaternion_x", "quaternion_y", "quaternion_z", "quaternion_w"], location_and_rotation)
        character_definition["data"] = resp

        return organize_success_response(character_definition)
    except Exception as e:
        return organize_failure_response(e)


# login to account
@app.route("/login", methods=["POST"])
def login():
    try:
        required_fields = ["username", "password"]
        fields = check_required_fields(request, required_fields)

        results = dbconn.execute_query("select password, salt, id from accounts where username=%(username)s", fields)
        if len(results) == 0:
            raise Exception("Account not found.")

        hashed_pw = results[0][0]
        salt = results[0][1]
        id = results[0][2]

        # return jsonify([bcrypt.hashpw(fields["password"].encode("utf-8"), salt), hashed_pw])
        if not bcrypt.hashpw(fields["password"].encode("utf-8"), salt).rstrip() == hashed_pw.rstrip():
            raise Exception("Incorrect password.")

        session = generate_session_id()

        # already have the session and everything, now supporting processes
        # query = "update accounts set last_login=now() where username=%(username)s"
        # dbconn.execute_action_query(query, fields)

        # doing this because I couldnt get na upsert to work
        existing_query = "select * from account_sessions where account_id=%(id)s"
        c = dbconn.execute_query(existing_query, {"id": id})
        query2 = ""
        if len(c) > 0:
            query2 = "update account_sessions set session=%(session)s, session_expire=now()+'1 hour' where account_id=%(id)s"
        else:
            query2 = "insert into account_sessions (account_id, session, session_expire) values (%(id)s, %(session)s, now() + '1 hour')"
        fields["id"] = id
        fields["session"] = str(session)
        dbconn.execute_action_query(query2, fields)
        sessions.append({"id": fields["id"], "session": fields["session"]})

        return organize_success_response(session)
    except Exception as e:
        return organize_failure_response(e)
    return


# logout of account
@app.route("/logout", methods=["POST"])
def logout():
    try:
        required_fields = ["session"]
        fields = check_required_fields(request, required_fields)

        query = "delete from account_sessions where session=%(session)s"
        dbconn.execute_action_query(query, {"session": fields["session"]})
        remove_session(fields["session"])

        return organize_success_response()
    except Exception as e:
        return organize_failure_response(e)


# get character creation specs
@app.route("/character_specs", methods=["GET"])
def character_specs():
    try:
        # get races
        race_query = "select id as race_id, name, description from races"
        race_results = dbconn.execute_query(race_query)
        final_race_results = parsing.format_all_responses(["race_id", "name", "description"], race_results)

        # get genders
        gender_query = "select id, name from genders"
        gender_results = dbconn.execute_query(gender_query)
        final_gender_results = parsing.format_all_responses(["id", "name"], gender_results)

        # get race models
        race_model_query = "select id, race_id, model_id from race_models"
        race_model_results = dbconn.execute_query(race_model_query)
        final_race_model_results = parsing.format_all_responses(["id", "race_id", "model_id"], race_model_results)

        # combine some extra fields
        for result in final_race_results:
            result["model_ids"] = list()

        for race_result in final_race_results:
            for model_result in final_race_model_results:
                if race_result["race_id"] == model_result["race_id"]:
                    race_result["model_ids"].append(model_result["id"])

        results = dict()
        results["races"] = final_race_results

        results["genders"] = final_gender_results

        return organize_success_response(results)
    except Exception as e:
        return organize_failure_response(e)


# main method
if __name__ == "__main__":
    app.run(host="localhost", port=8080)
