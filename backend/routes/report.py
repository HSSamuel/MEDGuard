import os
from flask import Blueprint, jsonify, request, current_app, session
from werkzeug.utils import secure_filename
from backend.database import get_db
from datetime import datetime
from backend.notifications import send_sms_alert # Import the new function

report_bp = Blueprint("report_api", __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Checks if a file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# =========================
# POST: Save a new counterfeit report (now with location data and user tracking)
# =========================
@report_bp.post("/report")
def create_report():
    # Get the user_id from the session if a user is logged in
    user_id = session.get("user_id")
    
    # Form data is now multipart/form-data, not JSON
    drug_name = request.form.get("drug_name")
    batch_number = request.form.get("batch_number")
    location = request.form.get("location")
    note = request.form.get("note")
    # ADDED: Get latitude and longitude from the form
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")
    image_file = request.files.get('image')

    if not batch_number:
        return jsonify({"message": "❌ Batch number is required"}), 400

    image_filename = None
    if image_file and allowed_file(image_file.filename):
        # Create a secure filename and save the image
        image_filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{image_file.filename}")
        upload_folder = os.path.join(current_app.static_folder, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)  # Ensure the directory exists
        image_file.save(os.path.join(upload_folder, image_filename))

    conn = get_db()
    # UPDATED: The INSERT statement now includes user_id, latitude and longitude
    conn.execute(
        """
        INSERT INTO reports (user_id, drug_name, batch_number, location, note, image_filename, latitude, longitude, reported_on, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, drug_name, batch_number, location, note, image_filename, latitude, longitude, datetime.now(), 0)
    )
    conn.commit()

    # --- NEW: Trigger SMS Alert ---
    report_data_for_alert = {
        "drug_name": drug_name,
        "batch_number": batch_number,
    }
    send_sms_alert(report_data_for_alert)
    # ----------------------------

    return jsonify({"message": "🚨 Report received. Thank you for helping keep patients safe."}), 201


# =========================
# GET: Fetch counterfeit reports (supports search & date filters)
# =========================
@report_bp.get("/report")
def get_reports():
    conn = get_db()
    search = request.args.get("search", "").strip()
    start = request.args.get("start", "").strip()
    end = request.args.get("end", "").strip()

    # Updated query to include the image_filename
    query = """
        SELECT id, drug_name, batch_number, location, note, image_filename, reported_on, status
        FROM reports
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (drug_name LIKE ? OR batch_number LIKE ? OR location LIKE ? OR note LIKE ?)"
        params.extend([f"%{search}%"] * 4)

    if start and end:
        query += " AND date(reported_on) BETWEEN date(?) AND date(?)"
        params.extend([start, end])

    query += " ORDER BY reported_on DESC"

    rows = conn.execute(query, params).fetchall()

    reports = [dict(row) for row in rows]
    for report in reports:
        report["status_label"] = "New" if report["status"] == 0 else "Checked"

    return jsonify(reports)


# =========================
# POST: Mark a report as Checked
# =========================
@report_bp.post("/report/<int:report_id>/mark_checked")
def mark_report_checked(report_id):
    try:
        conn = get_db()
        conn.execute("UPDATE reports SET status = 1 WHERE id = ?", (report_id,))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        print("Error updating report status:", e)
        return jsonify({"error": "Failed to update status"}), 500


# =========================
# GET: Count of New reports (for notification badge)
# =========================
@report_bp.get("/report/count")
def count_new_reports():
    conn = get_db()
    row = conn.execute("SELECT COUNT(*) as count FROM reports WHERE status = 0").fetchone()
    return jsonify({"count": row["count"] if row else 0})