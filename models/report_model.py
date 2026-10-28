from database.db_connection import get_connection, close_connection


def log_audit(user_id, action, medicine_id=None, changes=None):
    """Insert a row into audit_log."""
    conn = get_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO audit_log (user_id, medicine_id, action, changes)
               VALUES (%s, %s, %s, %s)""",
            (user_id, medicine_id, action, changes)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"[AUDIT ERROR] {e}")
        return False
    finally:
        close_connection(conn, cursor)


def get_audit_log(limit=100):
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT al.*, u.username,
                      COALESCE(m.name, 'Deleted') AS medicine_name
               FROM audit_log al
               JOIN user u ON al.user_id = u.id
               LEFT JOIN medicine m ON al.medicine_id = m.id
               ORDER BY al.performed_at DESC
               LIMIT %s""",
            (limit,)
        )
        return cursor.fetchall()
    finally:
        close_connection(conn, cursor)


def create_alert(medicine_id, alert_type, message=None):
    conn = get_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO alert (medicine_id, alert_type, message)
               VALUES (%s, %s, %s)""",
            (medicine_id, alert_type, message)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"[ALERT ERROR] {e}")
        return False
    finally:
        close_connection(conn, cursor)


def get_unresolved_alerts():
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT al.*, m.name AS medicine_name
               FROM alert al
               JOIN medicine m ON al.medicine_id = m.id
               WHERE al.is_resolved = 0
               ORDER BY al.created_at DESC"""
        )
        return cursor.fetchall()
    finally:
        close_connection(conn, cursor)


def resolve_alert(alert_id):
    conn = get_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            """UPDATE alert
               SET is_resolved = 1, resolved_at = CURRENT_TIMESTAMP
               WHERE id = %s""",
            (alert_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"[ALERT ERROR] {e}")
        return False
    finally:
        close_connection(conn, cursor)
