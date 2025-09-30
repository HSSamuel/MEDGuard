import requests
import re
from flask import Blueprint, render_template, request, url_for, current_app, session
from backend.database import get_db
from datetime import datetime, timedelta
from backend.emdex import get_drug_info_from_emdex
from math import radians, sin, cos, sqrt, atan2
from backend.blockchain_utils import query_chaincode

verify_bp = Blueprint("verify", __name__)

def haversine(lat1, lon1, lat2, lon2):
    """Calculate the distance between two points on Earth."""
    R = 6371
    dLat, dLon = radians(lat2 - lat1), radians(lon2 - lat1)
    a = sin(dLat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def check_scan_anomalies(conn, batch_number):
    """Analyze scan logs for suspicious activity."""
    logs = conn.execute(
        "SELECT latitude, longitude, scanned_at FROM scan_logs WHERE batch_number = ? ORDER BY scanned_at DESC",
        (batch_number,)
    ).fetchall()

    if len(logs) < 2:
        return None

    recent_scans = [log for log in logs if log['scanned_at'] > datetime.now() - timedelta(hours=1)]
    if len(recent_scans) > 50:
        return f"This code has been scanned an unusually high number of times ({len(recent_scans)} times in the last hour)."

    latest_log = logs[0]
    previous_log = logs[1]
    
    if latest_log['latitude'] and previous_log['latitude']:
        distance = haversine(latest_log['latitude'], latest_log['longitude'], previous_log['latitude'], previous_log['longitude'])
        time_diff = latest_log['scanned_at'] - previous_log['scanned_at']
        hours = time_diff.total_seconds() / 3600
        
        if hours > 0:
            speed = distance / hours
            if speed > 900:
                return (f"This code was recently scanned in two locations that are too far apart to be plausible "
                        f"({int(distance)} km apart in {int(hours*60)} minutes). This suggests the code has been cloned.")
    
    return None

@verify_bp.route("/<path:scanned_data>")
def verify_smart_scan(scanned_data):
    """
    Intelligently handles any scanned data, distinguishing between MedGuard batches,
    barcodes, and other QR types.
    """
    conn = get_db()
    data = scanned_data.strip()
    
    conn.execute(
        "INSERT INTO scan_logs (batch_number, ip_address, user_id) VALUES (?, ?, ?)",
        (data, request.remote_addr, session.get("user_id"))
    )
    conn.commit()
    
    anomaly_warning = check_scan_anomalies(conn, data)
    verified_on_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    row = conn.execute(
        "SELECT id, name AS drug_name, batch_number, mfg_date, expiry_date, manufacturer FROM drugs WHERE batch_number = ?", (data,)
    ).fetchone()

    if row:
        try:
            expiry_date = datetime.strptime(str(row["expiry_date"]), "%Y-%m-%d").date()
            status = "expired" if expiry_date < datetime.today().date() else "valid"
            
            blockchain_history = None
            if status == 'valid':
                blockchain_history = query_chaincode('query_drug_history', data)


            return render_template("verify.html", 
                                   status=status, 
                                   batch=row, 
                                   verified_on=verified_on_str, 
                                   anomaly_warning=anomaly_warning,
                                   blockchain_history=blockchain_history) # <-- Pass data to template
        except (ValueError, TypeError):
            return render_template("verify.html", status="notfound", error="Could not parse expiry date.", verified_on=verified_on_str)

    try:
        api_key = current_app.config.get("EMDEX_API_KEY")
        public_data = get_drug_info_from_emdex(api_key, data)
        if public_data:
            return render_template("verify.html", status="public_info_found", public_data=public_data, verified_on=verified_on_str, anomaly_warning=anomaly_warning)
    except Exception as e:
        print(f"An error occurred while calling the EMDEX service: {e}")

    if data.lower().startswith("http"):
        return render_template("verify.html", status="external_url", external_url=data, verified_on=verified_on_str, scan_type='QR code')

    if data.isnumeric():
        return render_template(
            "verify.html",
            status="unregistered_product_code",
            scanned_content=data,
            verified_on=verified_on_str,
            scan_type='Barcode'
        )
    else:
        return render_template(
            "verify.html",
            status="notfound",
            scanned_content=data,
            verified_on=verified_on_str,
            scan_type='QR code'
        )