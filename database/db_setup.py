from database.db_connection import get_connection, close_connection


TABLES = {}

TABLES['category'] = """
CREATE TABLE IF NOT EXISTS category (
    id   INT          NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

TABLES['manufacturer'] = """
CREATE TABLE IF NOT EXISTS manufacturer (
    id           INT          NOT NULL AUTO_INCREMENT,
    name         VARCHAR(150) NOT NULL UNIQUE,
    contact_info VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

TABLES['unit'] = """
CREATE TABLE IF NOT EXISTS unit (
    id   INT         NOT NULL AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

TABLES['user'] = """
CREATE TABLE IF NOT EXISTS user (
    id            INT          NOT NULL AUTO_INCREMENT,
    username      VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(150) DEFAULT NULL,
    email         VARCHAR(150) DEFAULT NULL UNIQUE,
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login    TIMESTAMP    NULL DEFAULT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

TABLES['medicine'] = """
CREATE TABLE IF NOT EXISTS medicine (
    id                  INT            NOT NULL AUTO_INCREMENT,
    name                VARCHAR(150)   NOT NULL,
    category_id         INT            NOT NULL,
    manufacturer_id     INT            NOT NULL,
    unit_id             INT            NOT NULL,
    quantity            INT            NOT NULL DEFAULT 0,
    expiry_date         DATE           NOT NULL,
    price               DECIMAL(10,2)  NOT NULL DEFAULT 0.00,
    batch_number        VARCHAR(100)   NOT NULL,
    low_stock_threshold INT            NOT NULL DEFAULT 10,
    created_at          TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_medicine_category     FOREIGN KEY (category_id)     REFERENCES category(id),
    CONSTRAINT fk_medicine_manufacturer FOREIGN KEY (manufacturer_id) REFERENCES manufacturer(id),
    CONSTRAINT fk_medicine_unit         FOREIGN KEY (unit_id)         REFERENCES unit(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

TABLES['audit_log'] = """
CREATE TABLE IF NOT EXISTS audit_log (
    id           INT         NOT NULL AUTO_INCREMENT,
    user_id      INT         NOT NULL,
    medicine_id  INT         DEFAULT NULL,
    action       VARCHAR(20) NOT NULL,
    changes      TEXT        DEFAULT NULL,
    performed_at TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_audit_user     FOREIGN KEY (user_id)     REFERENCES user(id),
    CONSTRAINT fk_audit_medicine FOREIGN KEY (medicine_id) REFERENCES medicine(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

TABLES['alert'] = """
CREATE TABLE IF NOT EXISTS alert (
    id           INT         NOT NULL AUTO_INCREMENT,
    medicine_id  INT         NOT NULL,
    alert_type   VARCHAR(20) NOT NULL,
    message      VARCHAR(255)        DEFAULT NULL,
    is_resolved  TINYINT(1)  NOT NULL DEFAULT 0,
    created_at   TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at  TIMESTAMP   NULL     DEFAULT NULL,
    PRIMARY KEY (id),
    CONSTRAINT fk_alert_medicine FOREIGN KEY (medicine_id) REFERENCES medicine(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

SEED_CATEGORIES = [
    'Antibiotics', 'Analgesics', 'Antivirals', 'Vitamins',
    'Antifungals', 'Cardiovascular', 'Diabetes', 'Other'
]

SEED_UNITS = ['tablets', 'capsules', 'bottles', 'vials', 'sachets', 'ampoules']

SEED_MANUFACTURERS = [
    ('Pfizer',            'www.pfizer.com'),
    ('Johnson & Johnson', 'www.jnj.com'),
    ('Novartis',          'www.novartis.com'),
    ('Roche',             'www.roche.com'),
    ('AstraZeneca',       'www.astrazeneca.com'),
    ('Generic/Other',     None),
]


def setup_database():
    """Create all tables and insert seed data."""
    conn = get_connection()
    if not conn:
        print("[SETUP] Failed to connect to database.")
        return False

    cursor = conn.cursor()
    try:
        for table_name, ddl in TABLES.items():
            cursor.execute(ddl)
            print(f"[SETUP] Table '{table_name}' ready.")

        # Seed categories
        for name in SEED_CATEGORIES:
            cursor.execute(
                "INSERT IGNORE INTO category (name) VALUES (%s)", (name,)
            )

        # Seed units
        for name in SEED_UNITS:
            cursor.execute(
                "INSERT IGNORE INTO unit (name) VALUES (%s)", (name,)
            )

        # Seed manufacturers
        for name, contact in SEED_MANUFACTURERS:
            cursor.execute(
                "INSERT IGNORE INTO manufacturer (name, contact_info) VALUES (%s, %s)",
                (name, contact)
            )

        conn.commit()
        print("[SETUP] Database setup complete.")
        return True

    except Exception as e:
        conn.rollback()
        print(f"[SETUP ERROR] {e}")
        return False
    finally:
        close_connection(conn, cursor)


if __name__ == "__main__":
    setup_database()
