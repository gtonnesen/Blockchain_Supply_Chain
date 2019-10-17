
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)  # instantiate flask app
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'home.login'

# configure Blueprints here...
from .views import home, transaction
app.register_blueprint(home)
app.register_blueprint(transaction)

# from ..app import models
# from ..app.models import seeds



