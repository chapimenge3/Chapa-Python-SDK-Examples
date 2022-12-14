import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from chapa import Chapa
from dotenv import load_dotenv

load_dotenv('../.env')
# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

# load secrets
CHAPA_API_KEY = os.getenv('CHAPA_API_KEY')
CHAPA_WEBHOOK_SECRET = os.getenv('CHAPA_WEBHOOK_SECRET')
APP_URL = os.getenv('APP_URL')

# init Chapa so we can use it later in our models
chapa = Chapa(CHAPA_API_KEY, response_format='obj')

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['APPLICATION_ROOT'] = '/flask'

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/flask')

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/flask')

    # blueprint for books
    from .book import router
    app.register_blueprint(router, url_prefix='/flask')

    return app