import requests
from flask import Blueprint, render_template, request, url_for, current_app
from backend.database import get_db
from datetime import datetime
from backend.emdex import get_drug_info_from_emdex # Import the new function

# The blueprint is already registered with a '/verify' prefix in app.py
verify_bp = Blueprint("verify", __name__)


@verify_bp.route("/<path:scanned_data>")
def verify_smart_scan(scanned_data):
    """
    This is the new "Smart Scan" endpoint. It intelligently handles any data
    scanned from a QR code by checking multiple sources.
    """
    conn = get_db()
    data = scanned_data.strip()
    verified_on_str = datetime.now().strftime("%B %d, %Y at %I:%M %p") + " in Lagos, Nigeria"
    
    # --- Logic Path 1: Check the MedGuard Database (Highest Trust) ---
    row = conn.execute(
        "SELECT name AS drug_name, batch_number, mfg_date, expiry_date, manufacturer FROM drugs WHERE batch_number = ?", (data,)
    ).fetchone()

    if row:
        # If a match is found, check if the drug is expired.
        try:
            expiry_date = datetime.strptime(str(row["expiry_date"]), "%Y-%m-%d").date()
            if expiry_date < datetime.today().date():
                return render_template("verify.html", status="expired", batch=row, verified_on=verified_on_str)
            else:
                return render_template("verify.html", status="valid", batch=row, verified_on=verified_on_str)
        except (ValueError, TypeError):
            return render_template("verify.html", status="notfound", error="Could not parse expiry date.", verified_on=verified_on_str)

    # --- UPDATED: Logic Path 2: Call the EMDEX Service ---
    try:
        api_key = current_app.config.get("EMDEX_API_KEY")
        public_data = get_drug_info_from_emdex(api_key, data)
        
        if public_data:
            # We found public info from our trusted source.
            return render_template("verify.html", status="public_info_found", public_data=public_data, verified_on=verified_on_str)

    except Exception as e:
        print(f"An error occurred while calling the EMDEX service: {e}")
        # If the service fails, we continue to the next logic path.

    # This block runs only if the drug was not found in the MedGuard database.
    try:
        nafdac_api_url = url_for('nafdac_api.lookup_drug', batch_number=data, _external=True)
        response = requests.get(nafdac_api_url, timeout=5) # Added a timeout for safety
        
        if response.status_code == 200:
            public_data = response.json()
            # We found public info, but it's not MedGuard-verified.
            return render_template("verify.html", status="public_info_found", public_data=public_data, verified_on=verified_on_str)
    except requests.exceptions.RequestException as e:
        print(f"Could not connect to the simulated NAFDAC API: {e}")

    # --- Logic Path 3: Check if it's a URL to an external website ---
    if data.lower().startswith("http://") or data.lower().startswith("https://"):
        return render_template("verify.html", status="external_url", external_url=data, verified_on=verified_on_str)

    # --- Logic Path 4: If it's none of the above, it's unrecognized ---
    return render_template(
        "verify.html",
        status="notfound",
        scanned_content=data,
        verified_on=verified_on_str
    )