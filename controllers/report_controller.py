from database.db_connection import get_connection, close_connection


def _fetch(query, params=()):
    conn = get_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    except Exception as e:
        print(f"[ReportController] query error: {e}")
        return []
    finally:
        close_connection(conn, cursor)


def get_transaction_log(date_from=None, date_to=None, action_type=None):
    clauses = []
    params  = []

    if date_from:
        clauses.append("DATE(a.performed_at) >= %s")
        params.append(str(date_from))
    if date_to:
        clauses.append("DATE(a.performed_at) <= %s")
        params.append(str(date_to))
    if action_type and action_type not in ("All Types", ""):
        clauses.append("UPPER(a.action) = UPPER(%s)")
        params.append(action_type)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""

    # When a medicine is deleted, medicine_id becomes NULL (ON DELETE SET NULL).
    # We fall back to extracting the name from the changes text column.
    sql = f"""
        SELECT
            a.id,
            a.action,
            COALESCE(
                m.name,
                CASE
                    WHEN a.changes LIKE 'Added medicine: %'
                        THEN SUBSTRING(a.changes, LENGTH('Added medicine: ') + 1)
                    WHEN a.changes LIKE 'Updated medicine: %'
                        THEN SUBSTRING(a.changes, LENGTH('Updated medicine: ') + 1)
                    WHEN a.changes LIKE 'Deleted medicine id: %'
                        THEN CONCAT('(deleted id: ',
                              SUBSTRING(a.changes, LENGTH('Deleted medicine id: ') + 1), ')')
                    ELSE a.changes
                END
            )                   AS medicine,
            a.changes           AS notes,
            u.username          AS performed_by,
            a.performed_at
        FROM audit_log a
        LEFT JOIN medicine m ON m.id = a.medicine_id
        LEFT JOIN user     u ON u.id = a.user_id
        {where}
        ORDER BY a.performed_at DESC
        LIMIT 500
    """
    return _fetch(sql, params)


def get_summary_stats(date_from=None, date_to=None):
    params_date = []
    date_clause = ""
    if date_from and date_to:
        date_clause = "AND DATE(performed_at) BETWEEN %s AND %s"
        params_date = [str(date_from), str(date_to)]

    def count_action(action):
        rows = _fetch(
            f"SELECT COUNT(*) AS c FROM audit_log WHERE UPPER(action)=UPPER(%s) {date_clause}",
            [action] + params_date
        )
        return int(rows[0]["c"]) if rows else 0

    rows = _fetch("SELECT COUNT(*) AS c FROM medicine")
    total_meds = int(rows[0]["c"]) if rows else 0

    return {
        "total_meds": total_meds,
        "added":      count_action("ADD"),
        "updated":    count_action("UPDATE"),
        "deleted":    count_action("DELETE"),
        "dispensed":  count_action("DISPENSE"),
        "stocked":    count_action("STOCK"),
    }


def get_action_types():
    rows = _fetch("SELECT DISTINCT action FROM audit_log ORDER BY action")
    return ["All Types"] + [r["action"] for r in rows]


def get_top_dispensed(date_from=None, date_to=None, limit=10):
    params = []
    date_clause = ""
    if date_from and date_to:
        date_clause = "AND DATE(a.performed_at) BETWEEN %s AND %s"
        params = [str(date_from), str(date_to)]
    sql = f"""
        SELECT m.name, COUNT(*) AS total_dispensed
        FROM audit_log a
        JOIN medicine m ON m.id = a.medicine_id
        WHERE a.action = 'DISPENSE' {date_clause}
        GROUP BY m.id, m.name
        ORDER BY total_dispensed DESC
        LIMIT {limit}
    """
    return _fetch(sql, params)