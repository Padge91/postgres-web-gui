import psycopg2


class DatabaseConnection(object):

    def __init__(self, database_host, database_port, database_user, database_password, database_name):
        self.database_host = database_host
        self.database_port = database_port
        self.database_user = database_user
        self.database_password = database_password
        self.database_name = database_name
        self.conn = None

    # test if the database is connected
    def is_connected(self):
        try:
            if self.conn is None:
                return False

            cursor = self.conn.cursor()
            cursor.execute("select 1")
            return True
        except Exception as e:
            return False

    # connect to the database
    def connect(self):
        try:
            self.conn = psycopg2.connect(host=self.database_host, port=self.database_port,
                                         user=self.database_user, password=self.database_password,
                                         database=self.database_name)
        except Exception as e:
            raise Exception("Error connecting to database: "+str(e))

    # close the database connection
    def disconnect(self):
        try:
            self.conn.close()
            self.conn = None
        except Exception as e:
            raise Exception("Error closing database: "+str(e))

    # execute a query to make changes
    def execute_action_query(self, query, params=None):
        try:
            # reconnect if connection is dead
            if not self.is_connected():
                self.connect()

            cursor = self.conn.cursor()
            if params is None:
                cursor.execute(query)
            else:
                cursor.execute(query, params)

            self.conn.commit()
            cursor.close()
        except Exception as e:
            raise Exception("Error executing action query: "+str(e))

    # execute a query to get results
    def execute_query(self, query, params=None):
        try:
            # reconnect if connection is dead
            if not self.is_connected():
                self.connect()

            cursor = self.conn.cursor()
            if params is None:
                cursor.execute(query)
            else:
                cursor.execute(query, params)

            db_response = cursor.fetchall()
            cursor.close()
            return db_response
        except Exception as e:
            # conn.rollback()
            raise Exception("Error executing query: " + str(e))