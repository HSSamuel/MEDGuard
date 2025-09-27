from backend.celery_init import celery_app
from flask_mail import Message
from backend.notifications import mail

@celery_app.task
def send_sms_alert_task(report_details):
    """Celery task to send an SMS alert."""
    from backend.app import create_app
    from backend.notifications import send_sms_alert
    app, _ = create_app()
    with app.app_context():
        send_sms_alert(report_details)

@celery_app.task
def send_email_alert_task(report_details):
    """Celery task to send an email alert."""
    from backend.app import create_app
    from backend.notifications import send_email_alert
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