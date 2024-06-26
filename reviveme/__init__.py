from flask import Flask
from flask_migrate import Migrate

from reviveme.db import db


def create_app(testing=False):
    app = Flask(__name__)
    app.config.from_pyfile("../config.py")

    if testing:
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"        
    else:
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {'connect_args': {'options': '-c timezone=utc'}}
        if app.config["ENVIRONMENT"] == 'development':
            app.config["SQLALCHEMY_ENGINE_OPTIONS"]['echo'] = True

    db.init_app(app)
    migrate = Migrate(app, db)

    # Register blueprints
    from reviveme.api.v1 import bp as v1_bp

    app.register_blueprint(v1_bp, url_prefix="/api/v1")

    @app.route("/")
    def index():
        return "suffix URL with /api/v1/{route} to use API"

    return app
