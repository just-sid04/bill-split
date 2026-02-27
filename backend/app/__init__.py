from flask_cors import CORS
from flask import Flask

from app.config import config
from app.extensions import db, ma
from app.routes import api


def create_app(config_name='default'):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    
    # Register blueprints
    app.register_blueprint(api)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app