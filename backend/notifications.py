import os
from twilio.rest import Client
from backend.config import get_config
from flask_mail import Mail, Message
from flask import current_app

cfg = get_config()
mail = Mail()

# IMPORTANT: You should set this as an environment variable in a real application
# This is the regulator's phone number that will receive the alert.
REGULATOR_PHONE_NUMBER = os.getenv("REGULATOR_PHONE_NUMBER") 
REGULATOR_EMAIL_ADDRESS = os.getenv("REGULATOR_EMAIL_ADDRESS")

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


def send_email_alert(report_details):
    """Sends an email alert to a regulator when a new report is submitted."""

    if not all([cfg.MAIL_USERNAME, cfg.MAIL_PASSWORD, REGULATOR_EMAIL_ADDRESS]):
        print("WARNING: Email credentials or regulator email address not configured. Skipping email alert.")
        return
        
    try:
        msg = Message(
            "New MedGuard Counterfeit Drug Report",
            sender=cfg.MAIL_USERNAME,
            recipients=[REGULATOR_EMAIL_ADDRESS]
        )
        msg.body = (
            f"A new counterfeit drug report has been submitted.\n\n"
            f"Drug Name: {report_details.get('drug_name', 'N/A')}\n"
            f"Batch Number: {report_details.get('batch_number')}\n\n"
            f"Please log in to the MedGuard admin dashboard to view the full report."
        )
        with current_app.app_context():
            mail.send(msg)
        print(f"Email alert sent successfully to {REGULATOR_EMAIL_ADDRESS}")
    except Exception as e:
        print(f"ERROR: Failed to send email alert - {e}")