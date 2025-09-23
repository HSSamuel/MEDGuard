import json
import os
from flask import Blueprint, jsonify, current_app

nafdac_api_bp = Blueprint("nafdac_api", __name__)

def load_public_db():
    """Loads the mock NAFDAC public database from its JSON file."""
    try:
        file_path = os.path.join(current_app.root_path, 'nafdac_public_db.json')
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR loading nafdac_public_db.json: {e}")
        return {}

@nafdac_api_bp.route("/nafdac/lookup/<string:batch_number>")
def lookup_drug(batch_number):
    """
    Simulates looking up a drug in the NAFDAC public database by reading from a JSON file.
    """
    public_db = load_public_db()
    drug_info = public_db.get(batch_number)
    
    if drug_info:
        return jsonify(drug_info)
    else:
        return jsonify({"error": "Drug not found in public registry"}), 404