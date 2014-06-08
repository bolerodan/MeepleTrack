import meeple
import datetime
import urllib2
from flask import request
from api_tools import api_package, api_error, api_error_missing, api_not_found, verify_email
from authentication import authenticate, authenticated_user
from crossdomain import crossdomain
from game import Game
from tools import build_search,build_game

from meeple_exceptions import GameNotFound
from sqlalchemy.exc import IntegrityError

@meeple.api.route('/search', endpoint="search", methods=['GET'])
@crossdomain(origin='*')
@authenticate
def search():
    r = []
    if 'q' not in request.args:
        return api_package(data=r)

    search_q = request.args['q']
    if search_q.strip() == '':
        return api_package(data=r)

    if 'type' not in request.args:
        return api_package(data=r)
    t = request.args['type'].lower()    
    
    if t.startswith('game'):
        try:
            bgg_results = build_search(search_q)
            for result in bgg_results:
                """
                    get the ID and see if it exists
                    in out DB, if not, build game from
                    bgg_results
                """
                game = Game.query.filter(Game.game_id == result['id']).first()
                if game is not None:
                    r.append(game.as_search())
                else:
                    try:
                        game = build_game(result['id'])
                        meeple.db.session.add(game)
                        meeple.db.session.commit()
                        r.append(game.as_search())
                    except GameNotFound as v:
                        pass
                    except IntegrityError as v:
                        """
                            Something bad happened here.. an ID already exists..rollback DB
                            so we dont have incomplete information from this error.
                        """
                        meeple.db.session.rollback()
        except urllib2.HTTPError as e:
            return api_error("There was an error communication with BGG",401)
    else:
        return api_error("Unknown search type",404)
    return api_package(data=r)