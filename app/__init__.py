from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)
    @app.route('/status')
    def status_check():
        return {"status": "ok", "message": "Api is running!"}
    
    return app