import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',          # change to your MySQL username
    'password': 'Galaxy18@',          # change to your MySQL password
    'database': 'placement_management'
}

def get_connection():
    """Returns a new MySQL connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def init_db():
    """Test connection on startup."""
    conn = get_connection()
    if conn:
        print("Connected to MySQL successfully.")
        conn.close()
    else:
        print("Failed to connect to MySQL.")
