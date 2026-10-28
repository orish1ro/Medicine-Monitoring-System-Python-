from database.db_connection import get_connection, close_connection


def add_medicine(name, category_id, manufacturer_id, unit_id,
                 quantity, expiry_date, price, batch_number,
                 low_stock_threshold=10):
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO medicine
               (name, category_id, manufacturer_id, unit_id,
                quantity, expiry_date, price, batch_number, low_stock_threshold)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (name, category_id, manufacturer_id, unit_id,
             quantity, expiry_date, price, batch_number, low_stock_threshold)
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"[MEDICINE MODEL ERROR] {e}")
        return None
    finally:
        close_connection(conn, cursor)


def get_all_medicines():
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT m.*, c.name AS category_name,
                      mf.name AS manufacturer_name,
                      u.name  AS unit_name
               FROM medicine m
               JOIN category     c  ON m.category_id     = c.id
               JOIN manufacturer mf ON m.manufacturer_id = mf.id
               JOIN unit         u  ON m.unit_id         = u.id
               ORDER BY m.name"""
        )
        return cursor.fetchall()
    finally:
        close_connection(conn, cursor)


def get_medicine_by_id(medicine_id):
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT m.*, c.name AS category_name,
                      mf.name AS manufacturer_name,
                      u.name  AS unit_name
               FROM medicine m
               JOIN category     c  ON m.category_id     = c.id
               JOIN manufacturer mf ON m.manufacturer_id = mf.id
               JOIN unit         u  ON m.unit_id         = u.id
               WHERE m.id = %s""",
            (medicine_id,)
        )
        return cursor.fetchone()
    finally:
        close_connection(conn, cursor)


def update_medicine(medicine_id, name, category_id, manufacturer_id,
                    unit_id, quantity, expiry_date, price,
                    batch_number, low_stock_threshold=10):
    conn = get_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            """UPDATE medicine
               SET name=%s, category_id=%s, manufacturer_id=%s, unit_id=%s,
                   quantity=%s, expiry_date=%s, price=%s,
                   batch_number=%s, low_stock_threshold=%s
               WHERE id=%s""",
            (name, category_id, manufacturer_id, unit_id,
             quantity, expiry_date, price,
             batch_number, low_stock_threshold, medicine_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"[MEDICINE MODEL ERROR] {e}")
        return False
    finally:
        close_connection(conn, cursor)


def delete_medicine(medicine_id):
    conn = get_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM medicine WHERE id = %s", (medicine_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"[MEDICINE MODEL ERROR] {e}")
        return False
    finally:
        close_connection(conn, cursor)


def search_medicines(query="", category_id=None):
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """SELECT m.*, c.name AS category_name,
                        mf.name AS manufacturer_name,
                        u.name  AS unit_name
                 FROM medicine m
                 JOIN category     c  ON m.category_id     = c.id
                 JOIN manufacturer mf ON m.manufacturer_id = mf.id
                 JOIN unit         u  ON m.unit_id         = u.id
                 WHERE 1=1"""
        params = []
        if query:
            sql += " AND (m.name LIKE %s OR mf.name LIKE %s OR m.batch_number LIKE %s)"
            like = f"%{query}%"
            params.extend([like, like, like])
        if category_id:
            sql += " AND m.category_id = %s"
            params.append(category_id)
        sql += " ORDER BY m.name"
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        close_connection(conn, cursor)


def get_expired_medicines():
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT m.*, c.name AS category_name, u.name AS unit_name
               FROM medicine m
               JOIN category c ON m.category_id = c.id
               JOIN unit     u ON m.unit_id     = u.id
               WHERE m.expiry_date < CURDATE()
               ORDER BY m.expiry_date"""
        )
        return cursor.fetchall()
    finally:
        close_connection(conn, cursor)


def get_expiring_soon_medicines(days=30):
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT m.*, c.name AS category_name, u.name AS unit_name
               FROM medicine m
               JOIN category c ON m.category_id = c.id
               JOIN unit     u ON m.unit_id     = u.id
               WHERE m.expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
               ORDER BY m.expiry_date""",
            (days,)
        )
        return cursor.fetchall()
    finally:
        close_connection(conn, cursor)


def get_low_stock_medicines():
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT m.*, c.name AS category_name, u.name AS unit_name
               FROM medicine m
               JOIN category c ON m.category_id = c.id
               JOIN unit     u ON m.unit_id     = u.id
               WHERE m.quantity <= m.low_stock_threshold
                 AND m.expiry_date >= CURDATE()
               ORDER BY m.quantity"""
        )
        return cursor.fetchall()
    finally:
        close_connection(conn, cursor)
