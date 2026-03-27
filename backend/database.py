import mysql.connector

def get_db():
    # Connect to MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",            # Replace with your MySQL username
        password="password", # Replace with your MySQL password
        database="placement_management"
    )
    return conn
