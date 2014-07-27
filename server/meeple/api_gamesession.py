import meeple
import datetime
from flask import request
from cerberus import Validator
from api_tools import api_package, api_error, api_validation_error,date_parse
from properties import PropertyDef,Property,GameSessionProperties
from flask.ext.security import auth_token_required,current_user
from sqlalchemy import or_,and_
from game_session import GameSession,GameSessionPlayers
from game import Game
from user import User
from friends import Friends
from tools import addplayer_helper

@meeple.api.route('/gamesession', endpoint="get_game_sessions", methods=['GET'])
@auth_token_required
def get_game_sessions():
    sessions = []
    user_id = current_user._get_current_object().id
    q = GameSession.query.outerjoin(GameSessionPlayers).filter(or_(GameSessionPlayers.user_id == user_id,GameSession.host_id == user_id)).order_by(GameSession.created).all()
    for session in q:
        sessions.append(session.as_dict())
    return api_package(data=sessions)

@meeple.api.route('/gamesession/<id>', endpoint="get_game_session", methods=['GET'])
@auth_token_required
def get_game_session(id):
    try:
        id = int(id)
    except ValueError as e:
        return api_error("ID values must be integers only.")

    game_session = GameSession.query.filter(GameSession.id == id).first()
    if game_session:
        return api_package(data=game_session.as_dict())
    else:
        return api_error("Cannot find a gamesession with that ID",404)



@meeple.api.route('/gamesession', endpoint="create_game_sessions", methods=['POST'])
@auth_token_required
def create_game_sessions():

    form = request.get_json()
    print form
    if form is None:
        return api_error("Invalid Request")

    schema = {
                'name':{'type':'string','empty':False},
                'game_id':{'type':'integer','required':True},
                'start_date':{'type':'string','empty':False},
                'host_is_playing':{'type':'boolean','required':True}
            }
    v = Validator(schema)
    if v.validate(form) is False:
        return api_validation_error(v.errors)    

    game = Game().query.filter_by(game_id=form['game_id']).first()
    if game is None:
        return api_error("There was an issue adding the game to this session.") #this probably shouldnt happen but, we should check anyways

    newgamesession = GameSession()
    user = current_user._get_current_object()

    if form['host_is_playing'] is True:
        newgamesession.players.append(user) #the user/host is also a player.
        addplayer_helper(newgamesession,user)

    newgamesession.host = user #attach this session to the user creating it, as they are the host.

    newgamesession.game = game #relate this gamesession to this board game

    #name is optional. If left empty, the board games name will be used instead.
    if 'name' in form:
        newgamesession.name = form['name']
    else:
        newgamesession.name = game.name

    #user can specify a future start date, otherwise utcnow() is used as default value in table.
    if 'start_date' in form:
        newgamesession.start_date = date_parse(form['start_date'])

    meeple.db.session.add(newgamesession)
    meeple.db.session.commit()
    return api_package(data=newgamesession.as_dict())


@meeple.api.route('/gamesession/<id>/addplayer', endpoint="add_player_to_session", methods=['POST'])
@auth_token_required
def add_player_to_session(id):    

    form = request.get_json()
    user = current_user._get_current_object()
    if form is None:
        return api_error("Invalid Request")
    try:
        id = int(id)
    except ValueError as e:
        return api_error("id values must be integers only.")

    schema = {
                'user_id':{'type':'integer','required':True}
            }
    v = Validator(schema)
    if v.validate(form) is False:
        return api_validation_error(v.errors)  

    gs = GameSession.query.filter_by(id=id).first()

    if gs is None:
        return api_error("Unable to find a game session by that id")

    new_player = Friends.query.filter(and_(Friends.user_id == user.id,Friends.friend_id == form['user_id'])).first()

    if new_player is None:
        return api_error("Unable to find player to add to this game session")  

    #check if this player is already in
    if new_player.friend in gs.players:
        return api_error("This player is already in this game session")

    gs.players.append(new_player.friend)

    player_props = addplayer_helper(gs,new_player.friend)
    meeple.db.session.commit()
    return api_package(data=player_props)    



@meeple.api.route('/gamesession/<id>/property', endpoint="gamesession_property", methods=['POST'])
@auth_token_required
def gamesession_property(id):
    """
    Always check if the user who is doing this,
    is the host
    """
    form = request.get_json()
    user = current_user
    if form is None:
        return api_error("Invalid Request")

    schema = {
                'user_id':{'type':'integer','required':True},
                'propertydef_id':{'type':'integer','required':True},
                'value':{'required':True}
            }
    v = Validator(schema)
    if v.validate(form) is False:
        return api_validation_error(v.errors)   

    gs = GameSession.query.filter_by(id=id,host_id=user.id).first()
    if gs is None:
        return api_error("Unable to find a game session by that ID")

    propdef = PropertyDef.query.filter(PropertyDef.propdef_id == form['propertydef_id']).first()
    if propdef is None:
        return api_error("Unknown property definition")

    player = User.query.filter(User.id == form['player_id']).first()
    if player is None:
        return api_error("Unknown user")

    new_prop = Property()
    new_prop.propdef = propdef
    value_result = new_prop.set_value(form['value'])
    if value_result is False:
        return api_error("Invalid type or mismatching property type.")
    meeple.db.session.add(new_prop)

    gsp = GameSessionProperties()
    gsp.gamesession = gs
    gsp.user = player
    gsp.property = new_prop
    meeple.db.session.add(gsp)
    meeple.db.session.commit()
    return api_package()
