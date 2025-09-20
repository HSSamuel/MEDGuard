import logging
import secrets
import time  # using timestamps for last_activity
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import timedelta

from flask import (
    Flask, jsonify, render_template, request,
    redirect, url_for, session, abort
)
from flask_cors import CORS
from werkzeug.security import check_password_hash

from backend.config import get_config
from backend.database import init_db, get_db, close_db
from backend.models import get_admin_by_email
from backend.routes.register import register_bp
from backend.routes.verify import verify_bp
from backend.routes.report import report_bp
from backend.routes.sms import sms_bp
from backend.routes.ai import ai_bp

# Optional admin blueprint
try:
    from backend.routes.admin import admin_bp
    HAS_ADMIN = True
except Exception:
    HAS_ADMIN = False

# Approved regulator email domains
ALLOWED_DOMAINS = {"nafdac.gov.ng",
                   "regulator.example.org"}  # adjust as needed


def email_allowed(email: str) -> bool:
    try:
        domain = email.split("@", 1)[1].lower()
        return domain in ALLOWED_DOMAINS
    except Exception:
        return False


def create_app() -> Flask:
    cfg = get_config()

    app = Flask(
        __name__,
        template_folder=str(cfg.TEMPLATES_DIR),
        static_folder=str(cfg.STATIC_DIR),
        static_url_path="/static",
    )
    app.config.from_object(cfg)

    # Session security
    app.config.update(
        SECRET_KEY=cfg.SECRET_KEY,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=not cfg.DEBUG,
        PERMANENT_SESSION_LIFETIME=timedelta(
            minutes=5),  # 5 min inactivity timeout
        SESSION_REFRESH_EACH_REQUEST=False
    )

    # Enable CORS for API routes
    CORS(app, resources={r"/api/*": {"origins": cfg.CORS_ORIGINS}})

    # Configure logging
    _configure_logging(app)

    # Initialize database
    init_db()

    # ✅ Ensure DB connections are closed after each request
    @app.teardown_appcontext
    def teardown_db(exception):
        close_db()

    # -------------------
    # Auth helpers
    # -------------------
    def require_regulator():
        if not session.get("admin_id") or session.get("admin_role") != "regulator":
            return redirect(url_for("admin_login"))

    # Track last activity for inactivity timeout
    @app.before_request
    def check_session_timeout():
        if "last_activity" in session:
            now = time.time()
            last = session["last_activity"]
            if now - last > 300:  # 5 minutes
                session.clear()
                return redirect(url_for("admin_login"))
        session["last_activity"] = time.time()

    # -------------------
    # Routes
    # -------------------
    @app.get("/health")
    def health():
        return {"status": "ok", "app": app.config.get("APP_NAME", "MedGuard")}

    @app.get("/")
    def root():
        return render_template("index.html")

    @app.route("/sms-check")
    def render_sms_check():
        return render_template("sms_check.html")

    # --- THIS ROUTE IS NOW CORRECTLY PLACED ---
    @app.route("/about")
    def about_page():
        return render_template("about.html")

    # Admin login
    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            if not email_allowed(email):
                return render_template("admin_login.html", error="Email domain not allowed")

            conn = get_db()
            user = get_admin_by_email(conn, email)
            if not user or not user["is_verified"] or user["role"] != "regulator":
                return render_template("admin_login.html", error="Invalid credentials")
            if not check_password_hash(user["password_hash"], password):
                return render_template("admin_login.html", error="Invalid credentials")

            session.clear()
            session["admin_id"] = user["id"]
            session["admin_role"] = user["role"]
            session["csrf"] = secrets.token_urlsafe(32)
            session["last_activity"] = time.time()
            return redirect(url_for("admin_api.admin_dashboard"))

        return render_template("admin_login.html")

    # Admin logout
    @app.post("/admin/logout")
    def admin_logout():
        if request.form.get("csrf") != session.get("csrf"):
            abort(400)
        session.clear()
        return redirect(url_for("admin_login"))

    # Admin UI route - This now points to the admin blueprint dashboard
    @app.get("/admin")
    def admin_ui_redirect():
        return redirect(url_for("admin_api.admin_dashboard"))


    # Register API blueprints
    app.register_blueprint(register_bp, url_prefix="/api")
    app.register_blueprint(report_bp, url_prefix="/api")
    app.register_blueprint(sms_bp, url_prefix="/api")
    app.register_blueprint(ai_bp, url_prefix="/api")
    app.register_blueprint(verify_bp, url_prefix="/verify")

    if HAS_ADMIN:
        app.register_blueprint(admin_bp, url_prefix="/admin")

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="Not Found"), 404
    # ... (other error handlers)

    return app


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
    app = create_app()
    app.run(
        host=app.config.get("HOST", "127.0.0.1"),
        port=app.config.get("PORT", 5000),
        debug=app.config.get("DEBUG", True),
    )