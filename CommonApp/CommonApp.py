from flask import Flask, jsonify, request, Blueprint, send_from_directory
import Database.queries as queries
import Database.parsing as parsing

from config import config
import Database.Connection


app = Blueprint("CommonApp", __name__, static_folder="../static")


# app folder
@app.route("/app/<path:path>", methods=["GET"])
def app_files(path):
    return send_from_directory("static/app", path)


# dependencies
@app.route("/lib/<path:path>", methods=["GET"])
def dependencies_files(path):
    return send_from_directory("static/lib", path)
