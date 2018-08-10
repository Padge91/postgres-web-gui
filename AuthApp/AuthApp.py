from flask import Flask, jsonify, request, Blueprint, send_from_directory
import Database.queries as queries
import Database.parsing as parsing

from config import config
import Database.Connection


app = Blueprint("AuthApp", __name__, static_folder="../static")


@app.route("/login", methods=["POST"])
def login():
    required_fields = ["username", "password"]
    return jsonify({"success":True, "message":{"username":"nick", "session":"fewfgewefgw"}})


@app.route("/logout", methods=["POST"])
def logout():
    return 0


@app.route("/groups", methods=["GET", "POST"])
def get_groups():
    if request.method == "POST":
        return 0
    elif request.method == "GET":
        return 0
    else:
        return 1


@app.route("/groups/<id>", methods=["POST", "PUT", "DELETE", "GET"])
def groups(id):
    if request.method == "POST":

        return 0
    elif request.method == "GET":
        return 0
    elif request.method == "DELETE":
        return 0
    elif request.method == "PUT":
        return 0
    else:
        return 1



@app.route("/add_user_to_group", methods=["POST"])
def add_user_to_group():
    return 0


@app.route("/remove_user_from_group", methods=["POST"])
def remove_user_from_group():
    return 0


@app.route("/get_my_groups", methods=["GET"])
def get_my_groups():
    return 0


@app.route("/get_user_groups", methods=["GET"])
def get_user_groups():
    return 0