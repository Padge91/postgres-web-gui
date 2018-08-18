
# db queries we are running

table_list_query="select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';"


table_definition_query='''
                select cols.column_name, cols.data_type, keys.fkey
                from information_schema.columns AS cols
                LEFT OUTER JOIN
                (select column_name, 'foreign_key' fkey from information_schema.key_column_usage where constraint_name IN (
                select constraint_name
                from information_schema.table_constraints AS constraints
                where constraints.constraint_type='FOREIGN KEY'
                and table_name=%(table)s)) as keys
                ON cols.column_name = keys.column_name
                where cols.table_name=%(table)s
                '''   


foreign_keys_query='''
        SELECT ccu.table_name AS foreign_table_name, kcu.column_name AS column_name,ccu.column_name AS foreign_column_name
        FROM
            information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
        WHERE constraint_type = 'FOREIGN KEY' AND tc.table_name=%(table)s AND kcu.column_name=%(column)s;
                '''


delete_row = "delete from %(table)s where id=%(id)s"


get_user_password_and_salt = "select password, salt from cbk_users where username=%(username)s"

check_if_user_exists = "select username from cbk_users where username=%(username)s"

insert_session = "update cbk_users set session=%(session)s, session_expire=to_timestamp(%(session_expire)s) where username=%(username)s"

get_list_of_users = "select username from cbk_users"

create_user = "insert into cbk_users(username, password, date_created, date_modified, admin, salt) values (%(username)s, %(password)s, to_timestamp(%(date_created)s), to_timestamp(%(date_created)s), FALSE, %(salt)s)"

get_user_by_session = "select username from cbk_users where session=%(session)s"

create_group = "insert into cbk_groups(name, date_created, date_modified) values (%(name)s, to_timestamp(%(date_created)s), to_timestamp(%(date_modified)s))"

check_if_group_exists = "select name from cbk_groups where name=%(name)s"

get_group_id = "select id from cbk_groups where name=%(name)s"

get_list_of_groups = "select name, id from cbk_groups"

get_group = "select name, date_created, date_modified from cbk_groups where id=%(id)s"

get_group_members = "select member_id from cbk_group_members where group_id=%(group_id)s"

get_user = "select username, date_created from cbk_users where id=%(id)s"

add_user_to_group = "insert into cbk_group_members(member_id, group_id) values (%(member_id)s, %(group_id)s)"

delete_group = "delete from cbk_groups where id=%(id)s"

delete_all_members = "delete from cbk_group_members where group_id=%(id)s"

delete_member = "delete from cbk_group_members where group_id=%(group_id)s and member_id=%(user_id)s"

is_group_member = "select member_id, group_id from cbk_group_members where group_id=%(group_id)s and member_id=%(user_id)s"

delete_user = "delete from cbk_users where id=%(id)s"

delete_all_user_members = "delete from cbk_group_members where member_id=%(id)s"

update_password = "update cbk_users set password=%(password), salt=%(salt)s, date_modified=to_timestamp(%(date_modified)s) where id=%(id)s"

