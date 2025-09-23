import os
from twilio.rest import Client
from backend.config import get_config

cfg = get_config()

# IMPORTANT: You should set this as an environment variable in a real application
# This is the regulator's phone number that will receive the alert.
REGULATOR_PHONE_NUMBER = os.getenv("REGULATOR_PHONE_NUMBER") 

def send_sms_alert(report_details):
    """Sends an SMS alert to a regulator when a new report is submitted."""
    
    # Check if Twilio is configured
    if not all([cfg.TWILIO_ACCOUNT_SID, cfg.TWILIO_AUTH_TOKEN, cfg.TWILIO_PHONE_NUMBER, REGULATOR_PHONE_NUMBER]):
        print("WARNING: Twilio credentials or regulator phone number not configured. Skipping SMS alert.")
        return

    try:
        client = Client(cfg.TWILIO_ACCOUNT_SID, cfg.TWILIO_AUTH_TOKEN)
        
        message_body = (
            f"New MedGuard Alert: A counterfeit report has been submitted.\n"
            f"Drug: {report_details.get('drug_name', 'N/A')}\n"
            f"Batch: {report_details.get('batch_number')}"
        )
        
        message = client.messages.create(
            body=message_body,
            from_=cfg.TWILIO_PHONE_NUMBER,
            to=REGULATOR_PHONE_NUMBER
        )
        print(f"SMS alert sent successfully to {REGULATOR_PHONE_NUMBER}. SID: {message.sid}")

    except Exception as e:
        print(f"ERROR: Failed to send SMS alert - {e}")