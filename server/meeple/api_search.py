import meeple
import datetime
import urllib2
from flask import request
from api_tools import api_package, api_error, api_error_missing, api_not_found, verify_email
from flask.ext.security import auth_token_required,current_user
from crossdomain import crossdomain
from game import Game
from tools import build_search,build_game

from meeple_exceptions import GameNotFound
from sqlalchemy.exc import IntegrityError

@meeple.api.route('/search', endpoint="search", methods=['GET'])
@crossdomain(origin='*')
@auth_token_required
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

        bgg_results = build_search(search_q,id_only=True)
        bgg_required_games = []        
        for result in bgg_results:
            print "FIND GAME LOCALLY",result
            """
                get the ID and see if it exists
                in out DB, if not, build game from
                bgg_results
            """
            game = Game.query.filter(Game.game_id == result).first()
            if game is not None:
                r.append(game.as_search())
            else:
                """
                put this ID in a list, because these games are not in our
                DB, so get these from bgg
                """
                bgg_required_games.append(result)

        if len(bgg_required_games) > 0:
            print "FINDING BGG GAMES",bgg_required_games
            try:
                try:
                    game = build_game(bgg_required_games,False)
                    for g in game:
                        meeple.db.session.add(g)
                        r.append(g.as_search())
                    meeple.db.session.commit()
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