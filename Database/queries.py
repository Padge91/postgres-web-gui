
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


