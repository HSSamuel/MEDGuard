from celery import Celery

# This creates the Celery instance that other parts of the application can import.
# The actual configuration with the Flask app will happen in the app factory.
celery_app = Celery(__name__, broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
