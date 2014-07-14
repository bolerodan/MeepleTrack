import settings
from flask import Flask, Blueprint
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required
from flask.ext.sqlalchemy import SQLAlchemy
from api_tools import JSONEncoder
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = "ALDHJ89734HASD&*(ASDKH!!!KADHJS"
app.config['SQLALCHEMY_DATABASE_URI'] = settings.connectstring
app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'Authorization'
app.json_encoder = JSONEncoder

api = Blueprint('api', __name__)
db = SQLAlchemy(app)
import api_authentication
import api_user
import api_gamesession
import api_games
import api_search
from user import User
from roles import Role

app.register_blueprint(api, url_prefix='/api')


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)