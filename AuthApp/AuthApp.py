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
        if session is None or len(session) == 0:
            raise Exception("Session is empty.")

        results = dbconn.execute_query(queries.get_user_by_session, {"session": session})
        if len(results) == 0:
            return True
        username = results[0][0]

        dbconn.execute_action_query(queries.insert_session, {"session":"", "session_expire":0, "username":username})
        return True
    except Exception as e:
        raise Exception("Session could not be removed: ."+str(e))


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


def change_user_password(id, password, password_confirm, dbconn):
    if password != password_confirm:
        raise Exception("Password fields must match.")

    salt = bcrypt.gensalt(config.hash_rounds_default)
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), salt)
    date_modified = time.time()

    dbconn.execute_action_query(queries.update_password, {"id":id, "password":hashed_pw.decode("utf-8"), "salt":salt.decode("utf-8"), "date_modified":date_modified})
    return


def get_list_of_users(dbconn):
    results = dbconn.execute_query(queries.get_list_of_users)

    clean_names = []
    for username in results:
        clean_names.append(username[0].strip())
    return clean_names


def create_group(group_name, dbconn):
    now_time = time.time()

    # check if group already exists
    results = dbconn.execute_query(queries.check_if_group_exists, {"name":group_name})
    if len(results) > 0:
        raise Exception("Group name is already in use.")

    # create
    dbconn.execute_action_query(queries.create_group, {"name":group_name, "date_created":now_time, "date_modified":now_time})

    # return id
    results = dbconn.execute_query(queries.get_group_id, {"name":group_name})
    if len(results) == 0:
        raise Exception("Group name not found. Internal error.")

    return results[0][0]


def get_list_of_groups(dbconn):
    results = dbconn.execute_query(queries.get_list_of_groups)

    clean_groups = []
    for group in results:
        clean_groups.append({"name":group[0].strip(), "id":group[1]})
    return clean_groups


def get_group_members(id, dbconn):
    members = []

    results = dbconn.execute_query(queries.get_group_members, {"group_id":id})
    if len(results) == 0:
        return members

    for member in results:
        members.append(get_user(member[0], dbconn))

    return members


def get_group(id, dbconn):
    response_dict = {}

    results = dbconn.execute_query(queries.get_group, {"id":id})
    if len(results) == 0:
        raise Exception("Group not found.")

    group_name = results[0][0].strip()
    date_created = results[0][1]
    date_modified = results[0][2]
    response_dict["group"] = {"name":group_name.strip(), "date_created":date_created, "date_modified":date_modified}

    # get members
    results = get_group_members(id, dbconn)
    response_dict["members"] = results

    return response_dict


def get_user(id, dbconn):
    results = dbconn.execute_query(queries.get_user, {"id":id})
    if len(results) == 0:
        raise Exception("User not found.")

    username = results[0][0].strip()
    date_created = results[0][1]

    return {"id":id, "username":username, "date_created":date_created}


def add_user_to_group(group_id, user_id, dbconn):
    results = dbconn.execute_query(queries.get_user, {"id":user_id})
    if len(results) == 0:
        raise Exception("User not found.")

    results = dbconn.execute_query(queries.get_group, {"id":group_id})
    if len(results) == 0:
        raise Exception("Group not found.")

    if is_member_of_group(group_id, user_id, dbconn):
        raise Exception("User is already a member of group.")

    dbconn.execute_action_query(queries.add_user_to_group, {"member_id":user_id, "group_id":group_id})

    return True


def is_member_of_group(group_id, user_id, dbconn):
    results = dbconn.execute_query(queries.is_group_member, {"group_id":group_id, "user_id":user_id})
    if len(results) > 0:
        return True
    else:
        return False


def delete_group(group_id, dbconn):
    # remove all members first
    dbconn.execute_action_query(queries.delete_all_members, {"id":group_id})

    # now remove group
    dbconn.execute_action_query(queries.delete_group, {"id":group_id})

    return True


def remove_user_from_group(group_id, user_id, dbconn):
    dbconn.execute_action_query(queries.delete_member, {"group_id":group_id, "user_id":user_id})
    return True


def delete_user(user_id, dbconn):
    # delete user memberships
    dbconn.execute_action_query(queries.delete_all_user_member, {"id":user_id})

    # delete user
    dbconn.execute_action_query(queries.delete_user, {"id":user_id})

    return True



