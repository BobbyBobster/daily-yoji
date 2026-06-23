from flask import Flask
from flask_cors import CORS
from sqlalchemy import create_engine

engine = create_engine("sqlite:///yoji.db", pool_pre_ping=True, echo=True)


def create_app():
    app = Flask(__name__)
    app.json.ensure_ascii = False
    CORS(app)

    from app.web import bp as web_bp

    app.register_blueprint(web_bp, url_prefix="/")

    from app.api import bp as api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    return app
