from Classes.Shared import *
import uuid, bcrypt
import Database.queries as queries
import time
import Classes.User
import config.config as config


def login(username, password, dbconn):
    # validate password
    results = dbconn.execute_query(queries.get_user_password_and_salt, {"username": username})
    if len(results) == 0:
        raise Exception("User not found.")
    hashed_value, salt = results[0]

    provided_pw = bcrypt.hashpw(password.strip().encode("utf-8"), salt.strip().encode("utf-8")).decode("utf-8")
    if hashed_value.strip() != provided_pw.strip():
        raise Exception("Incorrect password.")

    # create session and save it to database
    new_session = uuid.uuid4()
    session_expire = time.time()+config.session_length_in_seconds
    dbconn.execute_action_query(queries.insert_session, {"username":username, "session":str(new_session), "session_expire":session_expire})

    return {"username": username, "session": str(new_session), "session_expire":session_expire}


def logout(session, dbconn):
    # remove session from database
    try:
        user = Classes.User.User.load_by_session(session)
        user.session = None
        user.persist()
        return True
    except Exception as e:
        raise Exception("Session could not be removed.")


def create_user(username, password, password_confirm, dbconn, create_date=time.time()):
    if password != password_confirm:
        raise Exception("Password fields must match.")

    # check if user already exists
    results = dbconn.execute_query(queries.check_if_user_exists, {"username": username})
    if len(results) > 0:
        raise Exception("Username is already in use.")

    # hash password
    salt = bcrypt.gensalt(config.hash_rounds_default)
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), salt)

    # create
    dbconn.execute_action_query(queries.create_user, {"username":username, "password":hashed_pw.decode("utf-8"), "date_created":create_date, "salt":salt.decode("utf-8")})

    return True


def get_list_of_users(dbconn):
    results = dbconn.execute_query(queries.get_list_of_users)
    return results










