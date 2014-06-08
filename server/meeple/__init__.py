import settings
from flask import Flask, Blueprint
from flask.ext.sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = "ALDHJ89734HASD&*(ASDKH!!!KADHJS"
app.config['SQLALCHEMY_DATABASE_URI'] = settings.connectstring


api = Blueprint('api', __name__)
db = SQLAlchemy(app)
import api_authentication
import api_user
import api_gamesession
import api_games
import api_search

app.register_blueprint(api, url_prefix='/api')