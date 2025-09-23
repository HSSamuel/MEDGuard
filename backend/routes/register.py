from flask import Blueprint, request, jsonify
from sqlite3 import IntegrityError
from backend.models import insert_drug

register_bp = Blueprint("register_api", __name__)


@register_bp.post("/register")
def public_register():
    data = request.get_json(silent=True) or {}
    required = ["name", "batch_number",
                "mfg_date", "expiry_date", "manufacturer"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        insert_drug(
            data["name"],
            data["batch_number"],
            data["mfg_date"],
            data["expiry_date"],
            data["manufacturer"]
        )
    except IntegrityError:
        return jsonify({"error": "Batch number already exists"}), 409

    return jsonify({"message": "Batch registered successfully"})
