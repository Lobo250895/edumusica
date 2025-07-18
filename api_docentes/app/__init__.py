from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from api_docentes.config import Config 

db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)

    from .routes import api_blueprint, web_blueprint
    app.register_blueprint(api_blueprint)
    app.register_blueprint(web_blueprint)

    return app
