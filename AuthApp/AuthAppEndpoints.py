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


@app.route("/logout", methods=["POST"])
def logout():
    try:
        if config.cookie_name not in request.cookies:
            return jsonify(success_response(True))

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


@app.route("/groups", methods=["GET", "POST"])
def groups():
    if request.method == "POST":
        # create a group
        return 0
    elif request.method == "GET":
        # get all groups
        return 0
    else:
        return 1


@app.route("/groups/<id>", methods=["POST", "DELETE", "GET", "PUT"])
def groups_with_id(id):
    if request.method == "POST":
        # add a user to a group
        return 0
    elif request.method == "GET":
        # get a group
        return 0
    elif request.method == "DELETE":
        # delete a group
        return 0
    elif request.method == "PUT":
        # update a group
        return 0
    else:
        return 1


@app.route("/users", methods=["GET", "POST"])
def users():
    try:
        # create user
        if request.method == "POST":
            required_fields = ["username", "password", "passwordConfirm"]
            fields = check_required_fields(request, required_fields)
            results = AuthApp.create_user(fields["username"], fields["password"], fields["passwordConfirm"], dbconn)
            return jsonify(success_response(results))
        # get list of users
        elif request.method == "GET":
            results = AuthApp.get_list_of_users(dbconn)
            return jsonify(success_response(results))
        else:
            raise Exception("Something went very, very wrong. You should never see this...")
    except Exception as e:
        return jsonify(error_response(e))


@app.route("/users/<id>", methods=["GET", "POST", "DELETE", "PUT"])
def users_with_id(id):
    if request.method == "POST":
        # not sure yet
        return 0
    elif request.method == "GET":
        # get a user
        return 0
    elif request.method == "DELETE":
        # delete a user
        return 0
    elif request.method == "PUT":
        # update a user
        return 0
    else:
        return 1



