from flask import Blueprint, request, render_template, redirect, url_for, session, jsonify, current_app, abort
from werkzeug.security import generate_password_hash, check_password_hash
from backend.database import get_db
import sqlite3
from itsdangerous import URLSafeTimedSerializer
from backend.celery_worker import send_password_reset_email_task


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
    # MODIFIED: Select additional columns for a more detailed view
    reports = conn.execute(
        "SELECT id, drug_name, batch_number, location, note, reported_on, status FROM reports WHERE user_id = ? ORDER BY reported_on DESC",
        (user_id,)
    ).fetchall()

    return render_template("my_reports.html", reports=reports)

# NEW: Route for users to delete their own reports
@auth_bp.delete("/my-reports/delete/<int:report_id>")
def delete_my_report(report_id):
    if "user_id" not in session:
        return jsonify({"error": "Authentication required"}), 401

    user_id = session["user_id"]
    conn = get_db()

    # First, verify the report belongs to the logged-in user
    report = conn.execute("SELECT id FROM reports WHERE id = ? AND user_id = ?", (report_id, user_id)).fetchone()

    if not report:
        # If the report doesn't exist or doesn't belong to the user, deny the request
        return jsonify({"error": "Report not found or you do not have permission to delete it."}), 404

    try:
        # If verification passes, proceed with deletion
        conn.execute("DELETE FROM reports WHERE id = ? AND user_id = ?", (report_id, user_id))
        conn.commit()
        return jsonify({"message": "Report deleted successfully."})
    except Exception as e:
        print(f"Error deleting user report {report_id}: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user:
            s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
            token = s.dumps(email, salt='password-reset-salt')
            reset_link = url_for("auth.reset_password", token=token, _external=True)
            send_password_reset_email_task.delay(email, reset_link)

        # Show a generic message to prevent email enumeration
        return "If an account with that email exists, a password reset link has been sent."

    return render_template("forgot_password.html")

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)  # 1-hour expiry
    except:
        abort(404)

    if request.method == "POST":
        new_password = request.form.get("password")
        password_hash = generate_password_hash(new_password)
        conn = get_db()
        conn.execute("UPDATE users SET password_hash = ? WHERE email = ?", (password_hash, email))
        conn.commit()
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", token=token)