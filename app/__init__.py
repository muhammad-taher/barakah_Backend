from flask import Flask
from app.config import Config
from app.extensions import db, migrate, jwt, cors
import app.models

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.categories import categories_bp
    from app.routes.products import products_bp
    from app.routes.orders import orders_bp
    from app.routes.admin import admin_bp
    from app.routes.upload import upload_bp
    from app.routes.settings import settings_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(settings_bp)

    @app.route('/api/health')
    def health_check():
        return {'status': 'ok'}

    return app
