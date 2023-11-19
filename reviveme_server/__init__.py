from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from reviveme_server.models.base import BaseModel
db = SQLAlchemy(model_class=BaseModel)

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("../config.py")

    db.init_app(app)

    # Register blueprints
    from reviveme_server.api.v1 import bp as v1_bp
    app.register_blueprint(v1_bp, url_prefix='/api/v1')
    
    return app
