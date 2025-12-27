import os
from flask import Blueprint, request, jsonify, current_app
from backend.database import get_db
from backend.celery_worker import analyze_image_task # <-- Task import

analysis_bp = Blueprint("analysis_api", __name__)

@analysis_bp.route("/analyze-image/<int:report_id>", methods=['POST'])
def analyze_report_image(report_id):
    conn = get_db()
    report = conn.execute("SELECT image_filename FROM reports WHERE id = ?", (report_id,)).fetchone()

    if not report or not report["image_filename"]:
        return jsonify({"error": "No image found for this report"}), 404

    # This path is needed for Celery worker to access the image file
    image_path = os.path.join(current_app.static_folder, 'uploads', report["image_filename"])
    
    if not os.path.exists(image_path):
        return jsonify({"error": "Image file not found on server"}), 404

    # Trigger the background task (non-blocking)
    analyze_image_task.delay(report_id, image_path)
    
    # Immediately update the database to show analysis is in progress
    conn.execute(
        "UPDATE reports SET image_analysis_result = ? WHERE id = ?",
        ("Pending...", report_id)
    )
    conn.commit()

    # Respond immediately to the frontend
    return jsonify({"message": "Image analysis has started in the background. The results will be available shortly."})