import psycopg2

# connect, disconnect, and execute queries

conn = None

#test db connection to see if open or not
def is_connected():
	try:
		if conn is None:
			return False

		#this should throw an error if the connection is dead
		cursor = conn.cursor()
		cursor.execute("select 1")
		return True

	except Exception as e:
		return False


#just create a database connection
def connect_to_db():
        try:
                host="54.200.255.89"
                port="5432"
                user="test"
                db="postgres"
		password="***REMOVED***"

		global conn
                conn = psycopg2.connect(host=host, port=port, user=user, database=db, password=password)
                return conn
        except Exception as e:
                raise Exception("Error connecting to database: " + str(e))


#close database connection
def disconnect_from_db(conn):
        try:
                conn.close()
		conn = None
        except Exception as e:
                raise Exception("Error closing database");

#run a query and close the connection
def execute_query(query, params=None):
        try:
		#reconnect to database if we are disconnected
		if not is_connected():
			connect_to_db()

		global conn
                cursor = conn.cursor()
		if params is None:
                        cursor.execute(query)
                else:
                        cursor.execute(query, params)

                conn.commit()
                db_response = cursor.fetchall()
                cursor.close()
		return db_response
        except Exception as e:
		#conn.rollback()
                raise Exception("Error executing query: " + str(e))


#execute query that expects no response
def execute_action_query(query, params=None):
        try:
                #reconnect to database if we are disconnected
                if not is_connected():
                        connect_to_db()

                global conn
                cursor = conn.cursor()
                if params is None:
                        cursor.execute(query)
                else:
                        cursor.execute(query, params)

                conn.commit()
                cursor.close()
        except Exception as e:
                #conn.rollback()
                raise Exception("Error executing query: " + str(e))


