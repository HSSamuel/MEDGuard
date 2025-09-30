# backend/app.py

# =============================================================================
# M A I N   A P P L I C A T I O N   F I L E
# =============================================================================
# This file serves as the central entry point and controller for the MedGuard Flask application.
# It uses the "application factory" pattern (`create_app`) to initialize and configure the app.
# This approach allows for easier testing and management of different configurations.
#
# The file is responsible for:
#   - Initializing the Flask app and its extensions (like CORS).
#   - Setting up security features, including session management and domain restrictions.
#   - Defining core application routes (e.g., home page, login, logout).
#   - Registering all feature-specific blueprints (e.g., for admin, reporting, AI).
#   - Configuring application-wide logging and error handling.
# =============================================================================

# --- Core Python Libraries ---
import logging
import secrets
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import timedelta
from functools import wraps

# --- Flask and Third-Party Libraries ---
from flask import (
    Flask, jsonify, render_template, request,
    redirect, url_for, session, abort
)
from flask_cors import CORS
from werkzeug.security import check_password_hash
from flask_babel import Babel
from flask_socketio import SocketIO

# --- Application-Specific Imports ---
from backend.config import get_config
from backend.database import init_db, get_db, close_db
from backend.models import get_admin_by_email
from backend.routes.register import register_bp
from backend.routes.verify import verify_bp
from backend.routes.report import report_bp
from backend.routes.sms import sms_bp
from backend.routes.ai import ai_bp
from backend.routes.admin import admin_bp
from backend.routes.nafdac_api import nafdac_api_bp
from backend.routes.parser import parser_bp
from backend.routes.public_db_admin import public_db_admin_bp
from backend.routes.auth import auth_bp
from backend.routes.adr import adr_bp
from backend.routes.hotspot import hotspot_bp
from backend.notifications import mail

HAS_ADMIN = True

# --- Security Configuration ---
ALLOWED_DOMAINS = {"nafdac.gov.ng", "regulator.example.org"}

def email_allowed(email: str) -> bool:
    """A security utility to check if a user's email domain is in the approved list."""
    try:
        domain = email.split("@", 1)[1].lower()
        return domain in ALLOWED_DOMAINS
    except (IndexError, AttributeError):
        return False

# =============================================================================
# A P P L I C A T I O N   F A C T O R Y
# =============================================================================
def create_app():
    """
    Creates, configures, and returns the main Flask application instance.
    This is the core of the application factory pattern.
    """
    cfg = get_config()
    app = Flask(
        __name__,
        template_folder=str(cfg.TEMPLATES_DIR),
        static_folder=str(cfg.STATIC_DIR),
        static_url_path="/static",
    )
    app.config.from_object(cfg)
    
    socketio = SocketIO(app)

    app.config['LANGUAGES'] = ['en', 'yo', 'ha', 'ig'] # English, Yorùbá, Hausa, Igbo
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = str(cfg.TRANSLATIONS_DIR)

    app.config.update(
        SECRET_KEY=cfg.SECRET_KEY,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=not cfg.DEBUG,
        SESSION_REFRESH_EACH_REQUEST=False,
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=15)
    )

    CORS(app, resources={r"/api/*": {"origins": cfg.CORS_ORIGINS}})
    _configure_logging(app)
    init_db()
    
    def get_locale():
        if 'language' in session and session['language'] in app.config['LANGUAGES']:
            return session['language']
        return request.accept_languages.best_match(app.config['LANGUAGES'])

    babel = Babel(app, locale_selector=get_locale)
    mail.init_app(app)

    @app.context_processor
    def inject_locale():
        return dict(current_locale=get_locale())

    @app.teardown_appcontext
    def teardown_db(exception):
        close_db()

    def role_required(role):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if session.get("admin_role") != role:
                    abort(403)
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    @app.get("/health")
    def health():
        return {"status": "ok", "app": app.config.get("APP_NAME", "MedGuard")}

    @app.get("/")
    def root():
        return render_template("index.html")

    @app.route("/sms-check")
    def render_sms_check():
        return render_template("sms_check.html")

    @app.route("/about")
    def about_page():
        return render_template("about.html")
    
    @app.route("/report-adr/<int:drug_id>")
    def adr_report_form(drug_id):
        conn = get_db()
        drug = conn.execute("SELECT id, name, batch_number, manufacturer FROM drugs WHERE id = ?", (drug_id,)).fetchone()
        if not drug:
            abort(404)
        return render_template("adr_report.html", drug=drug)

    @app.route('/change-language/<lang>')
    def change_language(lang):
        if lang in app.config['LANGUAGES']:
            session['language'] = lang
        return redirect(request.referrer or url_for('root'))

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            if not email_allowed(email):
                return render_template("admin_login.html", error="Email domain not allowed")
            conn = get_db()
            user = get_admin_by_email(conn, email)
            if user and user["is_verified"] and user["role"] == "regulator" and check_password_hash(user["password_hash"], password):
                session.clear()
                session["admin_id"] = user["id"]
                session["admin_role"] = user["role"]
                session["csrf"] = secrets.token_urlsafe(32)
                session.permanent = True
                return redirect(url_for("admin_api.admin_dashboard"))
            else:
                return render_template("admin_login.html", error="Invalid credentials")
        return render_template("admin_login.html")

    @app.post("/admin/logout")
    def admin_logout():
        if request.form.get("csrf") != session.get("csrf"):
            abort(400)
        session.clear()
        return redirect(url_for("admin_login"))

    @app.get("/admin")
    def admin_ui_redirect():
        return redirect(url_for("admin_api.admin_dashboard"))

    app.register_blueprint(register_bp, url_prefix="/api")
    app.register_blueprint(report_bp, url_prefix="/api")
    app.register_blueprint(sms_bp, url_prefix="/api")
    app.register_blueprint(ai_bp, url_prefix="/api")
    app.register_blueprint(nafdac_api_bp, url_prefix="/api")
    app.register_blueprint(verify_bp, url_prefix="/verify")
    app.register_blueprint(parser_bp, url_prefix="/api")
    app.register_blueprint(public_db_admin_bp, url_prefix="/api")
    app.register_blueprint(auth_bp)
    app.register_blueprint(adr_bp)
    app.register_blueprint(hotspot_bp, url_prefix="/api")
    if HAS_ADMIN:
        app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404
        
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    return app, socketio

def _configure_logging(app: Flask) -> None:
    level = app.config.get("LOG_LEVEL", "INFO").upper()
    app.logger.setLevel(level)
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    ))
    app.logger.addHandler(console)
    log_dir = Path(".logs")
    log_dir.mkdir(exist_ok=True)
    file_handler = RotatingFileHandler(
        log_dir / "medguard.log", maxBytes=1_000_000, backupCount=3
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    ))
    app.logger.addHandler(file_handler)

if __name__ == "__main__":
    app, socketio = create_app()
    socketio.run(
        app,
        host=app.config.get("HOST", "127.0.0.1"),
        port=app.config.get("PORT", 5000),
        debug=app.config.get("DEBUG", True),
    )