from flask import Blueprint, request
from twilio.twiml.messaging_response import MessagingResponse
from backend.database import get_db
from datetime import datetime

sms_bp = Blueprint("sms_api", __name__)

@sms_bp.route("/sms", methods=['POST'])
def sms_reply():
    """Receive and process incoming SMS from Twilio."""
    incoming_msg = request.values.get('Body', '').strip()
    
    # Simple parsing: assume the message is just the batch number
    batch_number = incoming_msg

    # Create a response object to build the reply
    resp = MessagingResponse()
    
    if not batch_number:
        resp.message("Please send a batch number to verify. For example: BATCH12345")
        return str(resp)

    # --- Database Lookup Logic ---
    conn = get_db()
    row = conn.execute(
        "SELECT name, expiry_date, manufacturer FROM drugs WHERE batch_number = ?",
        (batch_number,)
    ).fetchone()

    if not row:
        reply_msg = f"MedGuard: Batch '{batch_number}' not found. This drug may be counterfeit. Please report it."
    else:
        try:
            expiry = datetime.strptime(row['expiry_date'], '%Y-%m-%d').date()
            if expiry < datetime.today().date():
                reply_msg = f"MedGuard ALERT: Batch '{batch_number}' ({row['name']}) has EXPIRED on {row['expiry_date']}."
            else:
                reply_msg = f"MedGuard OK: Batch '{batch_number}' is a valid batch of {row['name']} from {row['manufacturer']}. Expires {row['expiry_date']}."
        except (ValueError, TypeError):
            reply_msg = f"MedGuard: Could not verify expiry date for batch '{batch_number}'."
            
    resp.message(reply_msg)
    return str(resp)