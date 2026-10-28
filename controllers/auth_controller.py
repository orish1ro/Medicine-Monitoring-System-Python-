import hashlib
from database.db_connection import get_connection, close_connection


class AuthController:

    @staticmethod
    def login(username: str, password: str) -> dict:
        conn = get_connection()
        if not conn:
            return {"error": "Database connection failed."}
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id, username, password_hash, full_name FROM user WHERE username = %s",
                (username,)
            )
            user = cursor.fetchone()
            if not user:
                return {"error": "Invalid username or password."}

            hashed = AuthController._hash_password(password)
            if user["password_hash"] != hashed:
                return {"error": "Invalid username or password."}

            # Update last_login
            cursor.execute(
                "UPDATE user SET last_login = CURRENT_TIMESTAMP WHERE id = %s",
                (user["id"],)
            )
            conn.commit()

            return {
                "success":   True,
                "user_id":   user["id"],
                "username":  user["username"],
                "full_name": user["full_name"],
            }
        except Exception as e:
            print(f"[AuthController] login error: {e}")
            return {"error": str(e)}
        finally:
            close_connection(conn, cursor)

    # ── REGISTER ──────────────────────────────────────────────
    @staticmethod
    def register(full_name: str, username: str, email: str, password: str) -> dict:
        if len(username) < 3:
            return {"error": "Username must be at least 3 characters."}
        if len(password) < 4:
            return {"error": "Password must be at least 4 characters."}
        if "@" not in email:
            return {"error": "Please enter a valid email."}

        conn = get_connection()
        if not conn:
            return {"error": "Database connection failed."}
        cursor = conn.cursor(dictionary=True)
        try:
            # Check duplicate username
            cursor.execute("SELECT id FROM user WHERE username = %s", (username,))
            if cursor.fetchone():
                return {"error": "Username already exists."}

            # Check duplicate email
            cursor.execute("SELECT id FROM user WHERE email = %s", (email,))
            if cursor.fetchone():
                return {"error": "Email already registered."}

            hashed = AuthController._hash_password(password)
            cursor.execute(
                """INSERT INTO user (username, password_hash, full_name, email)
                   VALUES (%s, %s, %s, %s)""",
                (username, hashed, full_name, email)
            )
            conn.commit()
            return {"success": True, "user_id": cursor.lastrowid}

        except Exception as e:
            conn.rollback()
            print(f"[AuthController] register error: {e}")
            return {"error": str(e)}
        finally:
            close_connection(conn, cursor)

    # ── HASH ──────────────────────────────────────────────────
    @staticmethod
    def _hash_password(password: str) -> str:
        """SHA-256 hash — matches the existing hash in your DB."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()