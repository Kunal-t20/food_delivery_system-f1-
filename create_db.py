import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = "database.db"
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

# ---------- USERS ----------
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT CHECK(role IN ('donor','recipient','admin','inspector')) NOT NULL DEFAULT 'donor',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# ---------- WAREHOUSE ----------
cur.execute("""
CREATE TABLE IF NOT EXISTS warehouse (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT DEFAULT 'Central Warehouse',
    location TEXT NOT NULL,
    capacity INTEGER DEFAULT 1000,
    manager_id INTEGER,
    FOREIGN KEY (manager_id) REFERENCES users(id) ON DELETE SET NULL
);
""")

# ---------- FOOD ITEMS ----------
cur.execute("""
CREATE TABLE IF NOT EXISTS food_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donor_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    category TEXT CHECK(category IN ('edible','nonedible')) DEFAULT 'edible',
    quantity TEXT NOT NULL,
    status TEXT DEFAULT 'Pending Inspection',
    stored_in INTEGER DEFAULT 1,
    latitude REAL,
    longitude REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (stored_in) REFERENCES warehouse(id) ON DELETE SET NULL
);
""")

# ---------- INSPECTION RECORDS ----------
cur.execute("""
CREATE TABLE IF NOT EXISTS inspection_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_item_id INTEGER NOT NULL,
    inspector_id INTEGER NOT NULL,
    remarks TEXT,
    result TEXT CHECK(result IN ('Approved','Rejected')),
    inspected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (food_item_id) REFERENCES food_items(id) ON DELETE CASCADE,
    FOREIGN KEY (inspector_id) REFERENCES users(id) ON DELETE CASCADE
);
""")

# ---------- DELIVERIES ----------
cur.execute("""
CREATE TABLE IF NOT EXISTS deliveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_item_id INTEGER NOT NULL,
    recipient_id INTEGER NOT NULL,
    driver_name TEXT DEFAULT NULL,
    delivery_status TEXT DEFAULT 'Pending',
    pickup_latitude REAL,
    pickup_longitude REAL,
    drop_latitude REAL,
    drop_longitude REAL,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_at TIMESTAMP,
    delivered_at TIMESTAMP,
    FOREIGN KEY (food_item_id) REFERENCES food_items(id) ON DELETE CASCADE,
    FOREIGN KEY (recipient_id) REFERENCES users(id) ON DELETE CASCADE
);
""")

# ---------- Default Warehouse ----------
cur.execute("SELECT COUNT(*) FROM warehouse")
if cur.fetchone()[0] == 0:
    cur.execute("INSERT INTO warehouse (name, location, capacity) VALUES (?, ?, ?)", 
                ("Central Warehouse", "Default City", 1000))

# ---------- Default Admin ----------
ADMIN_EMAIL = "palakoturkar07@gmail.com"
ADMIN_PASSWORD = "palakadmin2025"

cur.execute("SELECT * FROM users WHERE email=?", (ADMIN_EMAIL,))
if not cur.fetchone():
    hashed = generate_password_hash(ADMIN_PASSWORD)
    cur.execute("INSERT INTO users (fullname,email,password,role) VALUES (?,?,?,?)",
                ("System Admin", ADMIN_EMAIL, hashed, "admin"))
    print(f"✅ Admin created: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")

# ---------- Default Inspector ----------
INSPECTOR_EMAIL = "inspector@frs.com"
INSPECTOR_PASSWORD = "inspect123"

cur.execute("SELECT * FROM users WHERE email=?", (INSPECTOR_EMAIL,))
if not cur.fetchone():
    hashed = generate_password_hash(INSPECTOR_PASSWORD)
    cur.execute("INSERT INTO users (fullname,email,password,role) VALUES (?,?,?,?)",
                ("Quality Inspector", INSPECTOR_EMAIL, hashed, "inspector"))
    print(f"✅ Inspector created: {INSPECTOR_EMAIL} / {INSPECTOR_PASSWORD}")

conn.commit()
conn.close()
print("✅ Database initialized successfully (database.db)")
