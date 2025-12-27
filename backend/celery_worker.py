import os
from flask_mail import Message
from backend.celery_init import celery_app
from backend.notifications import mail, send_sms_alert, send_email_alert
from backend.image_analyzer import analyze_image
from backend.database import get_db

# Note: The 'create_app' import is inside functions to prevent circular imports.

@celery_app.task
def send_sms_alert_task(report_details):
    """Celery task to send an SMS alert."""
    from backend.app import create_app
    app, _ = create_app()
    with app.app_context():
        send_sms_alert(report_details)

@celery_app.task
def send_email_alert_task(report_details):
    """Celery task to send an email alert."""
    from backend.app import create_app
    app, _ = create_app()
    with app.app_context():
        send_email_alert(report_details)

@celery_app.task
def send_password_reset_email_task(user_email, reset_link):
    """Celery task for sending a password reset email."""
    from backend.app import create_app
    app, _ = create_app()
    with app.app_context():
        msg = Message('Password Reset Request',
                      sender=app.config.get('MAIL_USERNAME'),
                      recipients=[user_email])
        msg.body = f'''To reset your password, visit the following link:
{reset_link}

If you did not make this request then simply ignore this email and no changes will be made.
'''
        mail.send(msg)

@celery_app.task
def analyze_image_task(report_id, image_path):
    """Celery task to analyze an image in the background."""
    from backend.app import create_app
    app, _ = create_app()
    
    with app.app_context():
        print(f"ASYNC TASK: Analyzing image for report {report_id} at path: {image_path}")
        
        # 1. Perform the simulated heavy analysis
        analysis_result = analyze_image(image_path)
        
        # 2. Store the result in the database
        conn = get_db()
        conn.execute(
            "UPDATE reports SET image_analysis_result = ? WHERE id = ?",
            (f"{analysis_result['label']} (Confidence: {analysis_result['confidence']:.2f})", report_id)
        )
        conn.commit()
        print(f"ASYNC TASK: Database updated for report {report_id}.")

        # 3. (Optional future feature: Emit WebSocket event to update admin UI instantly)
        # socketio.emit('analysis_complete', {'report_id': report_id, 'result': analysis_result['label']}, namespace='/')