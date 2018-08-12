from flask import Flask, jsonify, request
from CrudApp.CrudApp import app as crudapp
from AuthApp.AuthAppEndpoints import app as authapp
from CommonApp.CommonApp import app as commonapp

app = Flask(__name__)
app.register_blueprint(crudapp, url_prefix="/")
app.register_blueprint(authapp, url_prefix="/auth")
app.register_blueprint(commonapp, url_prefix="/static")


app.run(host="0.0.0.0", port=8080)
