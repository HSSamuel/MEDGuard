from flask import Blueprint, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database import get_db
import sqlite3

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not full_name or not email or not password:
            # You would typically use flash messages here for better UX
            return "All fields are required", 400

        password_hash = generate_password_hash(password)
        conn = get_db()

        try:
            conn.execute(
                "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
                (full_name, email, password_hash),
            )
            conn.commit()
            return redirect(url_for("auth.login"))
        except sqlite3.IntegrityError:
            return "An account with this email already exists.", 409

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["full_name"]
            return redirect(url_for("root"))
        else:
            return "Invalid email or password", 401
    
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("root"))

@auth_bp.route("/my-reports")
def my_reports():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    conn = get_db()
    reports = conn.execute(
        "SELECT * FROM reports WHERE user_id = ? ORDER BY reported_on DESC",
        (user_id,)
    ).fetchall()
    
    return render_template("my_reports.html", reports=reports)