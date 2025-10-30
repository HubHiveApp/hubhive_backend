from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt, socketio, cors

# blueprints
from .routes.auth       import auth_bp
from .routes.users      import users_bp
from .routes.chat       import chat_bp
from .routes.events     import events_bp
from .routes.businesses import businesses_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init extensions
    cors.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db, compare_type=True)
    jwt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # register routes
    app.register_blueprint(auth_bp,       url_prefix="/api/auth")
    app.register_blueprint(users_bp,      url_prefix="/api/users")
    app.register_blueprint(chat_bp,       url_prefix="/api/chat")
    app.register_blueprint(events_bp,     url_prefix="/api/events")
    app.register_blueprint(businesses_bp, url_prefix="/api/businesses")

    return app
