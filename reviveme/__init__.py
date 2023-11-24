from flask import Flask
from flask_migrate import Migrate

from reviveme.db import db


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("../config.py")

    db.init_app(app)
    migrate = Migrate(app, db)

    # Register blueprints
    from reviveme.api.v1 import bp as v1_bp

    app.register_blueprint(v1_bp, url_prefix="/api/v1")

    @app.route("/")
    def index():
        return "suffix URL with /api/v1/{route} to use API"

    return app
