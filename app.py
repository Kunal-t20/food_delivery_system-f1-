import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dotenv import load_dotenv

# ---------------- ENV ----------------
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "change_me_secret")
ADMIN_SECRET_CODE = os.getenv("ADMIN_SECRET_CODE", "admin_secret_code")

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = SECRET_KEY

DB_PATH = "database.db"

# ---------------- DB HELPERS ----------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def current_user():
    if "user_id" in session:
        return {
            "id": session["user_id"],
            "name": session.get("user_name"),
            "role": session.get("role"),
        }
    return None

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html", user=current_user())

# --------- Register ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "donor")

        if role not in ("donor", "recipient"):
            flash("Invalid role for public registration.", "danger")
            return redirect(url_for("register"))

        if not fullname or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        hashed = generate_password_hash(password)
        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (fullname, email, password, role, created_at) VALUES (?, ?, ?, ?, ?)",
                (fullname, email, hashed, role, datetime.now()),
            )
            conn.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already registered.", "danger")
        finally:
            conn.close()

    return render_template("register.html", user=current_user())

# --------- Login ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cur.fetchone()
        conn.close()

        if not user or not check_password_hash(user["password"], password):
            flash("Invalid credentials.", "danger")
            return redirect(url_for("login"))

        session.clear()
        session["user_id"] = user["id"]
        session["user_name"] = user["fullname"]
        session["role"] = user["role"]

        flash(f"Welcome, {user['fullname']}!", "success")

        role = user["role"]
        if role == "donor":
            return redirect(url_for("donor_dashboard"))
        elif role == "recipient":
            return redirect(url_for("recipient_dashboard"))
        elif role == "inspector":
            return redirect(url_for("inspector_dashboard"))
        elif role == "admin":
            return redirect(url_for("admin_dashboard"))
        else:
            return redirect(url_for("index"))

    return render_template("login.html", user=current_user())

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))

# --------- Admin Registration ----------
@app.route("/admin/register", methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        code = request.form.get("admin_code", "")
        if code != ADMIN_SECRET_CODE:
            flash("Invalid admin code.", "danger")
            return redirect(url_for("admin_register"))

        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not fullname or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("admin_register"))

        hashed = generate_password_hash(password)
        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (fullname, email, password, role, created_at) VALUES (?, ?, ?, 'admin', ?)",
                (fullname, email, hashed, datetime.now()),
            )
            conn.commit()
            flash("Admin user created successfully.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already exists.", "danger")
        finally:
            conn.close()

    return render_template("register.html", admin_register=True, user=current_user())

# ---------------- DONOR ----------------
@app.route("/donor")
def donor_dashboard():
    if "user_id" not in session or session.get("role") != "donor":
        return redirect(url_for("login"))

    uid = session["user_id"]
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM food_items WHERE donor_id = ? ORDER BY created_at DESC", (uid,))
    items = cur.fetchall()
    conn.close()

    return render_template("donor_dashboard.html", donations=items, user=current_user())

@app.route("/donor/donate", methods=["POST"])
def donate():
    if "user_id" not in session or session.get("role") != "donor":
        return redirect(url_for("login"))

    name = request.form.get("name", "").strip()
    quantity = request.form.get("quantity", "").strip()
    latitude = request.form.get("latitude", "").strip()
    longitude = request.form.get("longitude", "").strip()

    if not name or not quantity:
        flash("Food name and quantity are required.", "danger")
        return redirect(url_for("donor_dashboard"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO food_items 
           (donor_id, name, category, quantity, latitude, longitude, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, 'Pending Inspection', ?)""",
        (session["user_id"], name, "edible", quantity, latitude, longitude, datetime.now()),
    )
    conn.commit()
    conn.close()

    flash("Donation submitted (Pending Inspection).", "success")
    return redirect(url_for("donor_dashboard"))

# ---------------- INSPECTOR ----------------
@app.route("/inspector")
def inspector_dashboard():
    if "user_id" not in session or session.get("role") != "inspector":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT fi.*, u.fullname AS donor_name
           FROM food_items fi
           JOIN users u ON fi.donor_id = u.id
           WHERE fi.status = 'Pending Inspection'
           ORDER BY fi.created_at ASC"""
    )
    pending = cur.fetchall()

    cur.execute(
        """SELECT ir.*, fi.name AS food_name, u.fullname AS donor_name
           FROM inspection_records ir
           JOIN food_items fi ON ir.food_item_id = fi.id
           JOIN users u ON fi.donor_id = u.id
           WHERE ir.inspector_id = ?
           ORDER BY ir.inspected_at DESC""",
        (session["user_id"],),
    )
    my_inspections = cur.fetchall()
    conn.close()

    return render_template("inspector_dashboard.html", pending=pending, my_inspections=my_inspections, user=current_user())

@app.route("/inspect/<int:food_id>", methods=["POST"])
def inspect(food_id):
    if "user_id" not in session or session.get("role") != "inspector":
        return redirect(url_for("login"))

    result = request.form.get("result")
    remarks = request.form.get("remarks", "").strip()

    if result not in ("Approved", "Rejected"):
        flash("Invalid inspection result.", "danger")
        return redirect(url_for("inspector_dashboard"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO inspection_records (food_item_id, inspector_id, remarks, result, inspected_at) VALUES (?, ?, ?, ?, ?)",
        (food_id, session["user_id"], remarks, result, datetime.now()),
    )
    cur.execute("UPDATE food_items SET status = ? WHERE id = ?", (result, food_id))
    conn.commit()
    conn.close()

    flash(f"Inspection recorded: {result}", "success")
    return redirect(url_for("inspector_dashboard"))

# ---------------- RECIPIENT ----------------
@app.route("/recipient")
def recipient_dashboard():
    if "user_id" not in session or session.get("role") != "recipient":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()
    # Show approved donations
    cur.execute(
        "SELECT * FROM food_items WHERE status = 'Approved' ORDER BY created_at DESC"
    )
    available = cur.fetchall()
    conn.close()

    return render_template("recipient_dashboard.html", available_foods=available, user=current_user())

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin_dashboard():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users ORDER BY created_at DESC")
    users = cur.fetchall()

    cur.execute("SELECT * FROM food_items ORDER BY created_at DESC")
    food = cur.fetchall()

    conn.close()
    return render_template("admin_dashboard.html", users=users, food=food, user=current_user())

@app.route("/admin/manage-users")
def manage_users():
    if "user_id" not in session or session.get("role") != "admin":
        flash("Unauthorized access", "danger")
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, fullname, email, role, created_at FROM users ORDER BY created_at DESC")
    users = cur.fetchall()
    conn.close()

    return render_template("manage_users.html", users=users, user=current_user(), datetime=datetime)

@app.route("/claim/<int:food_id>", methods=["POST"])
def claim_food(food_id):
    if "user_id" not in session or session.get("role") != "recipient":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()

    # Check if food is available
    cur.execute("SELECT * FROM food_items WHERE id = ? AND status = 'Approved'", (food_id,))
    food = cur.fetchone()
    if not food:
        flash("Food item not available.", "danger")
        conn.close()
        return redirect(url_for("recipient_dashboard"))

    # Create delivery record
    cur.execute(
        """INSERT INTO deliveries (food_item_id, recipient_id, pickup_latitude, pickup_longitude)
           VALUES (?, ?, ?, ?)""",
        (food_id, session["user_id"], food["latitude"], food["longitude"])
    )
    cur.execute("UPDATE food_items SET status = 'Claimed' WHERE id = ?", (food_id,))
    conn.commit()
    conn.close()

    flash("Food claimed successfully! Await delivery assignment.", "success")
    return redirect(url_for("recipient_dashboard"))


@app.errorhandler(404)
def not_found(e):
    return render_template("index.html", user=current_user()), 404

if __name__ == "__main__":
    app.run(debug=True)
