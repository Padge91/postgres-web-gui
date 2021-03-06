# Postgres Web Interface

This application is a web interface for general Postgres usage. It allows for basic CRUD operations against a set of database tables, regardless of table schemas.

The `crudapp` directory contains the Flask app described above, as well as a WSGI script file for hosting the app behind Apache HTTP Server.

The front end of the application utilizes AngularJS for a dynamic interface, and primarily consumes AJAX from the back end.

Application was originally engineered for multiplayer server administration for easily creating, modifying, or deleting game objects. Code is built so it is abstract from implementation logic, so it works just as well for any other source database.
