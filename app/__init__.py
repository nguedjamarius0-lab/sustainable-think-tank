import os
from flask import Flask, request, session, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_babel import Babel
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
babel = Babel()
limiter = Limiter(key_func=get_remote_address)
cache = Cache()
csrf = CSRFProtect()


def get_locale():
    return session.get("lang", "fr")


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "default")

    app = Flask(__name__)

    from config import config
    app.config.from_object(config[config_name])

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    os.makedirs(app.config.get("UPLOAD_FOLDER", "app/static/uploads"), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app, locale_selector=get_locale)
    limiter.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(413)
    def too_large_error(error):
        return render_template("errors/413.html"), 413

    from app.routes.main import main_bp
    from app.routes.publications import publications_bp
    from app.routes.events import events_bp
    from app.routes.media import media_bp
    from app.routes.contact import contact_bp
    from app.routes.team import team_bp
    from app.routes.join import join_bp
    from app.routes.auth import auth_bp, admin_hidden_bp, oauth
    from app.routes.admin_views import admin_bp
    from app.routes.reseau import reseau_bp

    oauth.init_app(app)

    @app.route("/health")
    def health_check():
        return jsonify({"status": "ok"}), 200

    app.register_blueprint(main_bp)
    app.register_blueprint(publications_bp, url_prefix="/publications")
    app.register_blueprint(events_bp, url_prefix="/evenements")
    app.register_blueprint(media_bp, url_prefix="/medias")
    app.register_blueprint(contact_bp, url_prefix="/contact")
    app.register_blueprint(team_bp, url_prefix="/equipe")
    app.register_blueprint(join_bp, url_prefix="/agir")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_hidden_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(reseau_bp, url_prefix="/reseaux")

    return app
