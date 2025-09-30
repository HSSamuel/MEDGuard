import json
from flask import Blueprint, jsonify, current_app
import os

hotspot_bp = Blueprint("hotspot_api", __name__)

@hotspot_bp.route("/hotspots/predicted")
def get_predicted_hotspots():
    """
    API endpoint to provide the predicted hotspot data to the admin map.
    """
    try:
        file_path = os.path.join(current_app.root_path, 'predicted_hotspots.json')
        with open(file_path, 'r') as f:
            hotspots = json.load(f)
        return jsonify(hotspots)
    except FileNotFoundError:
        # If the prediction file doesn't exist, return an empty list
        return jsonify([])
    except Exception as e:
        print(f"Error reading predicted hotspots: {e}")
        return jsonify({"error": "Could not retrieve hotspot data"}), 500