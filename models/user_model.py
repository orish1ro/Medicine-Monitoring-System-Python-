from database.db_connection import get_connection, close_connection


def create_user(username, password_hash, full_name=None, email=None):
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO user (username, password_hash, full_name, email)
               VALUES (%s, %s, %s, %s)""",
            (username, password_hash, full_name, email)
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"[USER MODEL ERROR] {e}")
        return None
    finally:
        close_connection(conn, cursor)


def get_user_by_username(username):
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM user WHERE username = %s", (username,)
        )
        return cursor.fetchone()
    finally:
        close_connection(conn, cursor)


def get_user_by_id(user_id):
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM user WHERE id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        close_connection(conn, cursor)


def update_last_login(user_id):
    conn = get_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE user SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
            (user_id,)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"[USER MODEL ERROR] {e}")
        return False
    finally:
        close_connection(conn, cursor)


def get_all_users():
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, username, full_name, email, created_at, last_login FROM user")
        return cursor.fetchall()
    finally:
        close_connection(conn, cursor)
