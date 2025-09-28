# wsgi.py (Corrected)
from backend.app import create_app

app, socketio = create_app()
application = app