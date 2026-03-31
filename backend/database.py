import mysql.connector

def get_db():
    # Connect to MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",          # change if needed
        password="password",  # change this
        database="placement_management"
    )
    return conn