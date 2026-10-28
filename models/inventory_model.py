from database.db_connection import get_connection, close_connection


def get_all_categories():
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM category ORDER BY name")
        return cursor.fetchall()
    finally:
        close_connection(conn, cursor)


def get_all_units():
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM unit ORDER BY name")
        return cursor.fetchall()
    finally:
        close_connection(conn, cursor)


def get_all_manufacturers():
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM manufacturer ORDER BY name")
        return cursor.fetchall()
    finally:
        close_connection(conn, cursor)


def get_inventory_summary():
    """Returns counts for dashboard stat cards."""
    conn = get_connection()
    if not conn:
        return {}
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT
                COUNT(*)                                                      AS total,
                SUM(expiry_date < CURDATE())                                  AS expired,
                SUM(expiry_date BETWEEN CURDATE()
                    AND DATE_ADD(CURDATE(), INTERVAL 30 DAY))                 AS expiring_soon,
                SUM(quantity <= low_stock_threshold AND expiry_date >= CURDATE()) AS low_stock
               FROM medicine"""
        )
        return cursor.fetchone()
    finally:
        close_connection(conn, cursor)


def get_category_breakdown():
    """Returns medicine count per category — for the report bar chart."""
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT c.name AS category, COUNT(m.id) AS count
               FROM category c
               LEFT JOIN medicine m ON c.id = m.category_id
               GROUP BY c.id, c.name
               ORDER BY count DESC"""
        )
        return cursor.fetchall()
    finally:
        close_connection(conn, cursor)


def get_total_inventory_value():
    conn = get_connection()
    if not conn:
        return 0.0
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COALESCE(SUM(quantity * price), 0) FROM medicine")
        result = cursor.fetchone()
        return float(result[0]) if result else 0.0
    finally:
        close_connection(conn, cursor)
