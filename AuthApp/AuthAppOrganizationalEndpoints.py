from flask import Flask, jsonify, request, Blueprint, send_from_directory, make_response
import uuid, bcrypt
import Database.queries as queries
import Database.parsing as parsing
from Classes.Shared import *
import time

from config import config
import Database.Connection
import AuthApp.AuthApp as AuthApp


app = Blueprint("AuthApp", __name__, static_folder="../static")
dbconn = Database.Connection.DatabaseConnection(config.database_hostname,
            config.database_port, config.database_username,
            config.database_password, config.database_schema)
dbconn.connect()


# login
@app.route("/login", methods=["POST"])
def login():
    try:
        required_fields = ["username", "password"]
        fields = check_required_fields(request, required_fields)
        results = AuthApp.login(fields["username"], fields["password"], dbconn)

        # set cookie
        response = make_response(jsonify(success_response(results)))
        response.set_cookie(config.cookie_name, results["session"], expires=time.time()+config.session_length_in_seconds)

        return response
    except Exception as e:
        return jsonify(error_response(e))


# logout
@app.route("/logout", methods=["POST"])
def logout():
    try:
        if config.cookie_name not in request.cookies:
            raise Exception("No cookie provided.")

        session = request.cookies.get(config.cookie_name)
        if session is None or len(session) == 0:
            raise Exception("Session not found.")

        # remove from db
        AuthApp.logout(session, dbconn)

        # set cookie
        response = make_response(jsonify(success_response(True)))
        response.set_cookie(config.cookie_name, "", expires=0)

        return response
    except Exception as e:
        return jsonify(error_response(e))


# request access



# forgot password


# groups
@app.route("/groups", methods=["GET", "POST"])
@app.route("/groups/<id>", methods=["POST", "DELETE", "GET", "PUT"])
def groups(id=None):
    try:
        if request.method == "POST":
            if id is None:
                # create a group
                required_fields = ["groupName"]
                fields = check_required_fields(request, required_fields)
                group_id = AuthApp.create_group(fields["groupName"], dbconn)
                return jsonify(success_response(group_id))
            else:
                # add a user to a group
                required_fields = ["userId"]
                fields = check_required_fields(request, required_fields)
                AuthApp.add_user_to_group(id, fields["userId"], dbconn)
                return jsonify(success_response(True))
        elif request.method == "GET":
            if id is None:
                # get all groups
                results = AuthApp.get_list_of_groups(dbconn)
                return jsonify(success_response(results))
            else:
                # get a specific group
                results = AuthApp.get_group(id, dbconn)
                return jsonify(success_response(results))
        elif request.method == "DELETE":
            if not request.data:
                # delete a group
                AuthApp.delete_group(id, dbconn)
                return jsonify(success_response(True))
            else:
                # delete a group member
                required_fields = ["userId"]
                fields = check_required_fields(request, required_fields)
                AuthApp.remove_user_from_group(id, fields["userId"], dbconn)
                return jsonify(success_response(True))
        elif request.method == "PUT":
            # update a group
            # change name?
            # add user?
            return 0
        else:
            raise Exception("Something went very, very wrong. You should never see this...")
    except Exception as e:
        return jsonify(error_response(e))


# users
@app.route("/users", methods=["GET", "POST"])
@app.route("/users/<id>", methods=["GET", "POST", "DELETE", "PUT"])
def users(id=None):
    try:
        if request.method == "POST":
            # create a user
            required_fields = ["username", "password", "passwordConfirm"]
            fields = check_required_fields(request, required_fields)
            results = AuthApp.create_user(fields["username"], fields["password"], fields["passwordConfirm"], dbconn)
            return jsonify(success_response(results))
        elif request.method == "GET":
            if id is None:
                # get all users
                results = AuthApp.get_list_of_users(dbconn)
                return jsonify(success_response(results))
            else:
                # get a user
                user = AuthApp.get_user(id, dbconn)
                return jsonify(success_response(user))
        elif request.method == "DELETE":
            # delete a user
            AuthApp.delete_user(id, dbconn)
            return jsonify(success_response(True))
        elif request.method == "PUT":
            # update password
            required_fields = ["password", "passwordConfirm"]
            fields = check_required_fields(request, required_fields)
            AuthApp.change_user_password(id, fields["password"], fields["passwordConfirm"], dbconn)
            return jsonify(success_response(True))
        else:
            raise Exception("Something went very, very wrong. You should never see this...")
    except Exception as e:
        return jsonify(error_response(e))


# permissions
@app.route("/permissions", methods=["GET"])
@app.route("/permissions/<id>", methods=["GET", "DELETE", "PUT"])
def permissions(id=None):
    try:
        if request.method == "GET":
            if id is not None:
                # get permissions for a group
                results = AuthApp.get_group_permissions(id, dbconn)
                return jsonify(success_response(results))
            else:
                # get all permissions
                results = AuthApp.get_permissions(dbconn)
                return jsonify(success_response(results))
        elif request.method == "DELETE":
            # remove permissions from a group
            if not request.data:
                raise Exception("Must provide permission Id.")
            else:
                required_fields = ["permissionId"]
                fields = check_required_fields(request, required_fields)
                results = AuthApp.remove_permission_from_group(id, fields["permissionId"], dbconn)
                return jsonify(success_response(results))
        elif request.method == "PUT":
            # apply permission to group
            if not request.data:
                raise Exception("Must provide permission Id.")
            else:
                required_fields = ["permissionId", "objectLabel"]
                fields = check_required_fields(request, required_fields)
                results = AuthApp.add_permission_to_group(id, fields["permissionId"], fields["objectLabel"], dbconn)
                return jsonify(success_response(results))
        else:
            raise Exception("Something went very, very wrong. You should never see this...")
    except Exception as e:
        return jsonify(error_response(e))