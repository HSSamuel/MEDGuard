import re
from flask import Blueprint, request, jsonify
from urllib.parse import urlparse, parse_qs

parser_bp = Blueprint("parser_api", __name__)

def extract_manufacturer_from_domain(url):
    """A simple heuristic to guess a manufacturer's name from a URL's domain."""
    try:
        domain = urlparse(url).netloc
        company_name = domain.replace('www.', '').split('.')[0]
        return company_name.capitalize()
    except Exception:
        return ""

@parser_bp.route("/parse-qr", methods=['POST'])
def parse_qr_data():
    """
    Receives scanned QR data and intelligently extracts potential details
    to assist with registration.
    """
    scanned_data = request.json.get("data", "").strip()
    
    if not scanned_data:
        return jsonify({"error": "No data provided"}), 400

    details = { "batch_number": "", "manufacturer": "", "drug_name": "" }

    if scanned_data.startswith("http://") or scanned_data.startswith("https://"):
        details["manufacturer"] = extract_manufacturer_from_domain(scanned_data)
        query_params = parse_qs(urlparse(scanned_data).query)
        for key, value in query_params.items():
            if 'batch' in key.lower() or 'lot' in key.lower():
                details["batch_number"] = value[0]
                break
    else:
        details["batch_number"] = scanned_data

    return jsonify(details)

