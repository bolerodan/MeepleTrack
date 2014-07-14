import meeple
import datetime
from flask import request
from api_tools import api_package, api_error, api_error_missing, api_not_found, verify_email
from flask.ext.security import auth_token_required,current_user

from achievements import Achievement
from user import User
from game import Game
from tools import build_search,build_game

from meeple_exceptions import GameNotFound
from sqlalchemy.exc import IntegrityError

@meeple.api.route('/games', endpoint="get_games", methods=['GET'])
@auth_token_required
def get_games():
    search = request.args.get('search')
    results = build_search(search)
    return api_package(data=results)

@meeple.api.route('/games/<id>', endpoint="get_game", methods=['GET'])
#@authenticate
def get_game(id):
    try:
        id = int(id)
    except ValueError as e:
        return api_error("ID values must be integers only.")
    """
    Lets see if we can get this from our DB first
    """
    game = Game.query.filter(Game.game_id == id).first()
    if not game:  
        """
            We cant, so lets try to get it from BGG
        """
        try:    
            game = build_game(id,False)
            meeple.db.session.add(game)
            meeple.db.session.commit()
            return api_package(data=game.as_dict())
        except GameNotFound as v:
            #it doesnt exist at BGG so error out
            return api_error(str(v),404)
        except IntegrityError as v:
            """
                Something bad happened here.. an ID already exists..rollback DB
                so we dont have incomplete information from this error.
            """
            meeple.db.session.rollback()
            return api_error("There was a critical error grabbing this game",404)
    return api_package(data=game.as_dict())