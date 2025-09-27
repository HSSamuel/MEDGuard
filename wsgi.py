# wsgi.py

from backend.app import create_app

# Unpack the tuple from create_app and assign the app object to 'application'
application, _ = create_app()