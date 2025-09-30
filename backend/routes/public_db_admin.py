import json
import os
from flask import Blueprint, request, jsonify, current_app

public_db_admin_bp = Blueprint("public_db_admin_api", __name__)

def get_public_db_path():
    """Constructs the full, reliable path to the public database JSON file."""
    return os.path.join(current_app.root_path, 'nafdac_public_db.json')

def load_public_db():
    """Loads the public database from its JSON file."""
    try:
        with open(get_public_db_path(), 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR loading nafdac_public_db.json: {e}")
        return {}

def save_public_db(data):
    """Saves the provided data back to the public database JSON file."""
    try:
        with open(get_public_db_path(), 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"ERROR saving nafdac_public_db.json: {e}")
        return False

# --- API Endpoints for the Admin Interface ---

@public_db_admin_bp.route("/public-db", methods=['GET'])
def get_public_db():
    """API endpoint for the admin panel to fetch the current public drug data."""
    return jsonify(load_public_db())

@public_db_admin_bp.route("/public-db", methods=['POST'])
def update_public_db():
    """API endpoint for the admin panel to save the updated public drug data."""
    # UPDATED: More robust data handling
    try:
        updated_db = request.get_json()
        if updated_db is None:
            # Fallback for cases where the header might be incorrect
            data = request.data
            if not data:
                return jsonify({"status": "error", "message": "No data received"}), 400
            updated_db = json.loads(data)
    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid data format received"}), 400

    if save_public_db(updated_db):
        return jsonify({"status": "success", "message": "Public drug database updated successfully."})
    else:
        return jsonify({"status": "error", "message": "Failed to save public drug database to file."}), 500