from database.db_connection import get_connection, close_connection


class MedicineController:

    # ── FETCH ALL ─────────────────────────────────────────────
    @staticmethod
    def get_all_medicines():
        """Return all medicines joined with category, manufacturer, unit."""
        conn = get_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    m.id,
                    m.name,
                    m.category_id,
                    c.name        AS category,
                    m.manufacturer_id,
                    mf.name       AS manufacturer,
                    m.unit_id,
                    u.name        AS unit,
                    m.quantity,
                    m.expiry_date,
                    m.price,
                    m.batch_number,
                    m.low_stock_threshold,
                    m.created_at,
                    m.updated_at
                FROM medicine m
                JOIN category    c  ON m.category_id     = c.id
                JOIN manufacturer mf ON m.manufacturer_id = mf.id
                JOIN unit         u  ON m.unit_id          = u.id
                ORDER BY m.name ASC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"[MedicineController] get_all_medicines error: {e}")
            return []
        finally:
            close_connection(conn, cursor)

    # ── FETCH SINGLE ──────────────────────────────────────────
    @staticmethod
    def get_medicine_by_id(medicine_id: int):
        conn = get_connection()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    m.id, m.name,
                    m.category_id, c.name    AS category,
                    m.manufacturer_id, mf.name AS manufacturer,
                    m.unit_id, u.name         AS unit,
                    m.quantity, m.expiry_date,
                    m.price, m.batch_number,
                    m.low_stock_threshold
                FROM medicine m
                JOIN category     c  ON m.category_id     = c.id
                JOIN manufacturer mf ON m.manufacturer_id = mf.id
                JOIN unit         u  ON m.unit_id          = u.id
                WHERE m.id = %s
            """, (medicine_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"[MedicineController] get_medicine_by_id error: {e}")
            return None
        finally:
            close_connection(conn, cursor)

    # ── ADD ───────────────────────────────────────────────────
    @staticmethod
    def add_medicine(name, category_id, manufacturer_id, unit_id,
                     quantity, expiry_date, price, batch_number,
                     low_stock_threshold=10, user_id=None):
        conn = get_connection()
        if not conn:
            return {"error": "Database connection failed."}
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO medicine
                    (name, category_id, manufacturer_id, unit_id,
                     quantity, expiry_date, price, batch_number, low_stock_threshold)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, category_id, manufacturer_id, unit_id,
                  quantity, expiry_date, price, batch_number, low_stock_threshold))
            conn.commit()
            medicine_id = cursor.lastrowid

            # Audit log
            if user_id:
                MedicineController._log_audit(conn, user_id, medicine_id, "ADD",
                                               f"Added medicine: {name}")
            return {"success": True, "id": medicine_id}
        except Exception as e:
            conn.rollback()
            print(f"[MedicineController] add_medicine error: {e}")
            return {"error": str(e)}
        finally:
            close_connection(conn, cursor)

    # ── UPDATE ────────────────────────────────────────────────
    @staticmethod
    def update_medicine(medicine_id, name, category_id, manufacturer_id,
                        unit_id, quantity, expiry_date, price,
                        batch_number, low_stock_threshold=10, user_id=None):
        conn = get_connection()
        if not conn:
            return {"error": "Database connection failed."}
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE medicine SET
                    name                = %s,
                    category_id         = %s,
                    manufacturer_id     = %s,
                    unit_id             = %s,
                    quantity            = %s,
                    expiry_date         = %s,
                    price               = %s,
                    batch_number        = %s,
                    low_stock_threshold = %s
                WHERE id = %s
            """, (name, category_id, manufacturer_id, unit_id,
                  quantity, expiry_date, price, batch_number,
                  low_stock_threshold, medicine_id))
            conn.commit()

            if user_id:
                MedicineController._log_audit(conn, user_id, medicine_id, "UPDATE",
                                               f"Updated medicine: {name}")
            return {"success": True}
        except Exception as e:
            conn.rollback()
            print(f"[MedicineController] update_medicine error: {e}")
            return {"error": str(e)}
        finally:
            close_connection(conn, cursor)

    # ── DELETE ────────────────────────────────────────────────
    @staticmethod
    def delete_medicine(medicine_id, user_id=None):
        conn = get_connection()
        if not conn:
            return {"error": "Database connection failed."}
        cursor = conn.cursor(dictionary=True)
        try:
            # Fetch name BEFORE deleting so audit log has it
            cursor.execute("SELECT name FROM medicine WHERE id = %s", (medicine_id,))
            row = cursor.fetchone()
            med_name = row["name"] if row else f"id:{medicine_id}"

            cursor.execute("DELETE FROM medicine WHERE id = %s", (medicine_id,))
            conn.commit()

            if user_id:
                # Use None for medicine_id — FK is gone after delete, would cause constraint error
                MedicineController._log_audit(conn, user_id, None,
                                               "DELETE", f"Deleted medicine: {med_name}")
            return {"success": True}
        except Exception as e:
            conn.rollback()
            print(f"[MedicineController] delete_medicine error: {e}")
            return {"error": str(e)}
        finally:
            close_connection(conn, cursor)

    # ── SEARCH ────────────────────────────────────────────────
    @staticmethod
    def search_medicines(query="", category_id=None):
        conn = get_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            sql = """
                SELECT m.id, m.name, c.name AS category,
                       mf.name AS manufacturer, u.name AS unit,
                       m.quantity, m.expiry_date, m.price, m.batch_number
                FROM medicine m
                JOIN category     c  ON m.category_id     = c.id
                JOIN manufacturer mf ON m.manufacturer_id = mf.id
                JOIN unit         u  ON m.unit_id          = u.id
                WHERE (m.name LIKE %s OR mf.name LIKE %s OR m.batch_number LIKE %s)
            """
            params = [f"%{query}%", f"%{query}%", f"%{query}%"]
            if category_id:
                sql += " AND m.category_id = %s"
                params.append(category_id)
            sql += " ORDER BY m.name ASC"
            cursor.execute(sql, params)
            return cursor.fetchall()
        except Exception as e:
            print(f"[MedicineController] search error: {e}")
            return []
        finally:
            close_connection(conn, cursor)

    # ── DASHBOARD STATS ───────────────────────────────────────
    @staticmethod
    def get_dashboard_stats():
        conn = get_connection()
        if not conn:
            return {"total": 0, "expired": 0, "expiring": 0, "low_stock": 0}
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN expiry_date < CURDATE() THEN 1 ELSE 0 END) AS expired,
                    SUM(CASE WHEN expiry_date BETWEEN CURDATE()
                             AND DATE_ADD(CURDATE(), INTERVAL 30 DAY) THEN 1 ELSE 0 END) AS expiring,
                    SUM(CASE WHEN quantity <= low_stock_threshold
                             AND expiry_date >= CURDATE() THEN 1 ELSE 0 END) AS low_stock
                FROM medicine
            """)
            row = cursor.fetchone()
            return {
                "total":     int(row["total"]     or 0),
                "expired":   int(row["expired"]   or 0),
                "expiring":  int(row["expiring"]  or 0),
                "low_stock": int(row["low_stock"] or 0),
            }
        except Exception as e:
            print(f"[MedicineController] get_dashboard_stats error: {e}")
            return {"total": 0, "expired": 0, "expiring": 0, "low_stock": 0}
        finally:
            close_connection(conn, cursor)

    # ── FETCH LOOKUPS ─────────────────────────────────────────
    @staticmethod
    def get_categories():
        return MedicineController._fetch_lookup("SELECT id, name FROM category ORDER BY name")

    @staticmethod
    def get_manufacturers():
        return MedicineController._fetch_lookup("SELECT id, name FROM manufacturer ORDER BY name")

    @staticmethod
    def get_units():
        return MedicineController._fetch_lookup("SELECT id, name FROM unit ORDER BY name")

    @staticmethod
    def _fetch_lookup(sql):
        conn = get_connection()
        if not conn:
            return []
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"[MedicineController] lookup error: {e}")
            return []
        finally:
            close_connection(conn, cursor)

    # ── AUDIT LOG ─────────────────────────────────────────────
    @staticmethod
    def _log_audit(conn, user_id, medicine_id, action, changes):
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO audit_log (user_id, medicine_id, action, changes)
                VALUES (%s, %s, %s, %s)
            """, (user_id, medicine_id, action, changes))
            conn.commit()
            cur.close()
        except Exception as e:
            print(f"[MedicineController] audit log error: {e}")