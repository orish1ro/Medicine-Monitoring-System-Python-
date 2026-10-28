import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


def get_connection():
    """Return a new MySQL connection using config settings."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[DB ERROR] Could not connect: {e}")
        return None


def close_connection(conn, cursor=None):
    """Safely close cursor and connection."""
    if cursor:
        cursor.close()
    if conn and conn.is_connected():
        conn.close()

print("Database connected successfully!")