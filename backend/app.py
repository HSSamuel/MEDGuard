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

# --- Flask and Third-Party Libraries ---
from flask import (
    Flask, jsonify, render_template, request,
    redirect, url_for, session, abort
)
from flask_cors import CORS
from werkzeug.security import check_password_hash

# --- Application-Specific Imports ---
# Imports configuration, database handlers, and data models
from backend.config import get_config
from backend.database import init_db, get_db, close_db
from backend.models import get_admin_by_email

# Imports the blueprints that contain the routes for each feature
from backend.routes.register import register_bp
from backend.routes.verify import verify_bp
from backend.routes.report import report_bp
from backend.routes.sms import sms_bp
from backend.routes.ai import ai_bp
from backend.routes.admin import admin_bp
from backend.routes.nafdac_api import nafdac_api_bp # For the external lookup simulation
from backend.routes.parser import parser_bp
from backend.routes.public_db_admin import public_db_admin_bp
from backend.routes.auth import auth_bp
from backend.routes.analysis import analysis_bp

# A flag to check if the admin blueprint was imported successfully
HAS_ADMIN = True

# --- Security Configuration ---
# A whitelist of approved email domains for regulator accounts to prevent unauthorized sign-ups.
ALLOWED_DOMAINS = {"nafdac.gov.ng",
                   "regulator.example.org"}  # Can be expanded as needed

def email_allowed(email: str) -> bool:
    """A security utility to check if a user's email domain is in the approved list."""
    try:
        domain = email.split("@", 1)[1].lower()
        return domain in ALLOWED_DOMAINS
    except (IndexError, AttributeError):
        # Handles cases where the email format is invalid
        return False

# =============================================================================
# A P P L I C A T I O N   F A C T O R Y
# =============================================================================
def create_app() -> Flask:
    """
    Creates, configures, and returns the main Flask application instance.
    This is the core of the application factory pattern.
    """
    # --- App Initialization and Configuration ---
    cfg = get_config()
    app = Flask(
        __name__,
        template_folder=str(cfg.TEMPLATES_DIR),
        static_folder=str(cfg.STATIC_DIR),
        static_url_path="/static",
    )
    app.config.from_object(cfg)

    # --- Session and Security Configuration ---
    # These settings help protect against common web vulnerabilities.
    app.config.update(
        SECRET_KEY=cfg.SECRET_KEY,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=not cfg.DEBUG,
        SESSION_REFRESH_EACH_REQUEST=False
    )

    # --- Extensions and Core Services ---
    CORS(app, resources={r"/api/*": {"origins": cfg.CORS_ORIGINS}}) # Enables Cross-Origin Resource Sharing for APIs
    _configure_logging(app) # Sets up the application's logging system
    init_db() # Initializes the database tables if they don't exist

    # --- Request and Teardown Handlers ---
    @app.teardown_appcontext
    def teardown_db(exception):
        """Ensures the database connection is closed after each request to free up resources."""
        close_db()

    # =============================================================================
    # C O R E   R O U T E S
    # =============================================================================

    @app.get("/health")
    def health():
        """A simple health check endpoint to confirm the application is running."""
        return {"status": "ok", "app": app.config.get("APP_NAME", "MedGuard")}

    @app.get("/")
    def root():
        """Serves the main public-facing home page (index.html)."""
        return render_template("index.html")

    @app.route("/sms-check")
    def render_sms_check():
        """Renders the admin page for simulating SMS verification."""
        return render_template("sms_check.html")

    @app.route("/about")
    def about_page():
        """Serves the 'About MedGuard' informational page."""
        return render_template("about.html")

    # --- Admin Authentication Routes ---
    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        """Handles the regulator login process, including form submission and validation."""
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            if not email_allowed(email):
                return render_template("admin_login.html", error="Email domain not allowed")

            conn = get_db()
            user = get_admin_by_email(conn, email)

            # Securely checks the provided password against the stored hash
            if user and user["is_verified"] and user["role"] == "regulator" and check_password_hash(user["password_hash"], password):
                session.clear()
                session["admin_id"] = user["id"]
                session["admin_role"] = user["role"]
                session["csrf"] = secrets.token_urlsafe(32)
                return redirect(url_for("admin_api.admin_dashboard"))
            else:
                return render_template("admin_login.html", error="Invalid credentials")

        return render_template("admin_login.html")

    @app.post("/admin/logout")
    def admin_logout():
        """Handles the admin logout process by clearing the session."""
        if request.form.get("csrf") != session.get("csrf"):
            abort(400)
        session.clear()
        return redirect(url_for("admin_login"))

    @app.get("/admin")
    def admin_ui_redirect():
        """Redirects the base '/admin' URL to the admin dashboard for a cleaner user experience."""
        return redirect(url_for("admin_api.admin_dashboard"))

    # =============================================================================
    # B L U E P R I N T   R E G I S T R A T I O N
    # =============================================================================
    # Each blueprint is a self-contained feature. Registering them here connects them to the main app.
    app.register_blueprint(register_bp, url_prefix="/api")
    app.register_blueprint(report_bp, url_prefix="/api")
    app.register_blueprint(sms_bp, url_prefix="/api")
    app.register_blueprint(ai_bp, url_prefix="/api")
    app.register_blueprint(nafdac_api_bp, url_prefix="/api") # Connects the simulated NAFDAC API
    app.register_blueprint(verify_bp, url_prefix="/verify") # User-facing, so no /api prefix
    app.register_blueprint(parser_bp, url_prefix="/api")
    app.register_blueprint(public_db_admin_bp, url_prefix="/api")
    app.register_blueprint(auth_bp)  # No prefix, handles /login, /register, etc.
    app.register_blueprint(analysis_bp, url_prefix="/api")

    if HAS_ADMIN:
        app.register_blueprint(admin_bp, url_prefix="/admin")

    # =============================================================================
    # E R R O R   H A N D L E R S
    # =============================================================================
    # Defines how the application responds to common HTTP errors.
    @app.errorhandler(404)
    def not_found(e):
        """Returns a user-friendly 404 Not Found page."""
        return jsonify(error="Not Found"), 404
    # ... (other error handlers can be added here)

    return app

# =============================================================================
# H E L P E R   F U N C T I O N S
# =============================================================================
def _configure_logging(app: Flask) -> None:
    """Configures application-wide logging to both the console and a rotating file."""
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

# --- Application Runner ---
# This block allows you to run the app directly using `python run.py` for local development.
if __name__ == "__main__":
    app = create_app()
    app.run(
        host=app.config.get("HOST", "127.0.0.1"),
        port=app.config.get("PORT", 5000),
        debug=app.config.get("DEBUG", True),
    )
