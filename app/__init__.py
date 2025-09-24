import os
import logging
from flask import Flask, g, request
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from app.extensions import db

def create_app(config=None):
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create the Flask app with templates from the app directory
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Configure proxy support for Replit environment
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Configure the app - Require SESSION_SECRET for security
    app.secret_key = os.environ.get("SESSION_SECRET")
    if not app.secret_key:
        raise ValueError("SESSION_SECRET environment variable is required for security")
    
    # Database configuration
    # Use PostgreSQL in production, SQLite in development
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            # Heroku postgres:// format -> postgresql:// for SQLAlchemy
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_recycle": 300,
            "pool_pre_ping": True,
        }
    else:
        # Use SQLite in a subdirectory of app
        basedir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(basedir, 'database', 'yks_takip.db')
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize extensions
    db.init_app(app)

    # Development auto-login configuration (disabled by default)
    app.config["AUTO_LOGIN_ENABLED"] = str(os.environ.get("AUTO_LOGIN_ENABLED", "")).lower() in {"1", "true", "yes", "on"}
    app.config["AUTO_LOGIN_EMAIL"] = os.environ.get("AUTO_LOGIN_EMAIL", "dev.admin@example.com")
    app.config["AUTO_LOGIN_PASSWORD"] = os.environ.get("AUTO_LOGIN_PASSWORD", "devpass123")
    app.config["AUTO_LOGIN_AD"] = os.environ.get("AUTO_LOGIN_AD", "Geliştirici")
    app.config["AUTO_LOGIN_SOYAD"] = os.environ.get("AUTO_LOGIN_SOYAD", "Admin")

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Lütfen giriş yapın.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from app.blueprints.auth.models import User
        return User.query.get(int(user_id))

    # Register template filters
    from app.utils.filters import register_filters
    register_filters(app)

    # Register context processors
    @app.context_processor
    def inject_utilities():
        from app.utils.session import get_aktif_ogrenci
        return dict(get_aktif_ogrenci=get_aktif_ogrenci)

    with app.app_context():
        # Import route modules BEFORE registering blueprints
        # to ensure routes are registered with the blueprint
        from app.blueprints.auth import routes, auth_bp
        from app.blueprints.ana_sayfa import routes, ana_sayfa_bp
        from app.blueprints.ogrenci_yonetimi import routes, ogrenci_yonetimi_bp
        from app.blueprints.ders_konu_yonetimi import routes, ders_konu_yonetimi_bp
        from app.blueprints.deneme_sinavlari import routes, deneme_sinavlari_bp
        from app.blueprints.rapor_yonetimi import routes, rapor_yonetimi_bp
        from app.blueprints.calisma_programi import routes, routes_api, calisma_programi_bp
        from app.blueprints.parametre_yonetimi import routes, parametre_yonetimi_bp
        from app.blueprints.ilk_kayit_formu import routes, ilk_kayit_formu_bp
        from app.blueprints.gorusme_defteri import routes, gorusme_defteri_bp
        from app.blueprints.etkinlik_kayit import routes, etkinlik_kayit_bp
        from app.blueprints.anket_yonetimi import routes, anket_yonetimi_bp
        from app.blueprints.yapay_zeka_asistan import routes, yapay_zeka_asistan_bp

        # Register blueprints
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(ana_sayfa_bp)
        app.register_blueprint(ogrenci_yonetimi_bp, url_prefix='/ogrenci-yonetimi')
        app.register_blueprint(ders_konu_yonetimi_bp, url_prefix='/ders-konu-yonetimi')
        app.register_blueprint(deneme_sinavlari_bp, url_prefix='/deneme-sinavlari')
        app.register_blueprint(rapor_yonetimi_bp, url_prefix='/rapor-yonetimi')
        app.register_blueprint(calisma_programi_bp, url_prefix='/calisma-programi')
        app.register_blueprint(parametre_yonetimi_bp, url_prefix='/parametre-yonetimi')
        app.register_blueprint(ilk_kayit_formu_bp, url_prefix='/ilk-kayit-formu')
        app.register_blueprint(gorusme_defteri_bp, url_prefix='/gorusme-defteri')
        app.register_blueprint(etkinlik_kayit_bp, url_prefix='/etkinlik-kayit')
        app.register_blueprint(anket_yonetimi_bp, url_prefix='/anket-yonetimi')
        app.register_blueprint(yapay_zeka_asistan_bp, url_prefix='/yapay-zeka-asistan')

        # Import all models to ensure they are created
        from app.blueprints.auth.models import User
        from app.blueprints.ogrenci_yonetimi.models import Ogrenci
        # Import other models as needed...

        # Create all database tables
        db.create_all()

        # Ensure a development user exists when auto-login is enabled
        if app.config["AUTO_LOGIN_ENABLED"]:
            try:
                dev_user = User.query.filter_by(email=app.config["AUTO_LOGIN_EMAIL"].lower()).first()
                if dev_user is None:
                    dev_user = User(
                        email=app.config["AUTO_LOGIN_EMAIL"].lower(),
                        ad=app.config["AUTO_LOGIN_AD"],
                        soyad=app.config["AUTO_LOGIN_SOYAD"],
                        aktif=True,
                    )
                    dev_user.set_password(app.config["AUTO_LOGIN_PASSWORD"])
                    db.session.add(dev_user)
                    db.session.commit()
            except Exception:
                db.session.rollback()

    # Auto-login for development if enabled
    if app.config["AUTO_LOGIN_ENABLED"]:
        @app.before_request
        def _auto_login_dev_user():
            from flask_login import current_user, login_user
            # Skip static files and logout route to avoid interfering
            if request.endpoint in {"static"}:
                return None
            if request.endpoint == 'auth.logout':
                return None
            if getattr(current_user, 'is_authenticated', False):
                return None
            try:
                from app.blueprints.auth.models import User
                user = User.query.filter_by(email=app.config["AUTO_LOGIN_EMAIL"].lower()).first()
                if user and user.aktif:
                    login_user(user, remember=True)
            except Exception:
                return None
    
    return app
