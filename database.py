import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self):
        self.connection = self.connect_to_database()

    def connect_to_database(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="password123@",
                database="store"
            )
            if connection.is_connected():
                print("Connecté à la base de données MySQL")
                return connection
        except Error as e:
            print("Erreur :", e)

    def execute_query(self, query, data=None):
        cursor = self.connection.cursor()
        try:
            if data:
                cursor.execute(query, data)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor
        except Error as e:
            print(f"Error executing query: {e}")
            return None

    def fetch_all(self, query, data=None):
        cursor = self.execute_query(query, data)
        if cursor:
            return cursor.fetchall()
        return None

    def close_connection(self):
        if self.connection.is_connected():
            self.connection.close()
            print("Connection closed")
