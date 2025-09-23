import os
from flask import Blueprint, request, jsonify, current_app
from backend.database import get_db
from backend.image_analyzer import analyze_image

analysis_bp = Blueprint("analysis_api", __name__)

@analysis_bp.route("/analyze-image/<int:report_id>", methods=['POST'])
def analyze_report_image(report_id):
    conn = get_db()
    report = conn.execute("SELECT image_filename FROM reports WHERE id = ?", (report_id,)).fetchone()

    if not report or not report["image_filename"]:
        return jsonify({"error": "No image found for this report"}), 404

    image_path = os.path.join(current_app.static_folder, 'uploads', report["image_filename"])
    
    if not os.path.exists(image_path):
        return jsonify({"error": "Image file not found on server"}), 404

    # Get the analysis result
    analysis_result = analyze_image(image_path)
    
    # Store the result in the database
    conn.execute(
        "UPDATE reports SET image_analysis_result = ? WHERE id = ?",
        (f"{analysis_result['label']} (Confidence: {analysis_result['confidence']:.2f})", report_id)
    )
    conn.commit()

    return jsonify(analysis_result)