import meeple
import datetime
import urllib2
from cerberus import Validator
from flask import request
from api_tools import api_package, api_error,api_validation_error, api_error_missing, api_not_found, verify_email
from flask.ext.security import auth_token_required,current_user
from sqlalchemy import  or_,and_
from crossdomain import crossdomain
from user import User
from friends import Friends,FriendsGroup


@meeple.api.route('/friends', endpoint="friends", methods=['GET'])
@crossdomain(origin='*')
@auth_token_required
def friends():
    user = current_user._get_current_object()
    q = Friends.query.filter(Friends.user_id == user.id).all()    
    friends = []
    for f in q:
        friends.append(f.friend.as_minimal_dict())

    return api_package(data=friends)


@meeple.api.route('/friends/groups', endpoint="friend_groups", methods=['GET'])
@crossdomain(origin='*')
@auth_token_required
def friend_groups():
    user = current_user._get_current_object()    
    q = FriendsGroup.query.filter(FriendsGroup.user_id == user.id).all()    
    groups = []
    for g in q:
        groups.append(g.as_dict())

    return api_package(data=groups)


@meeple.api.route('/friends/groups', endpoint="create_friends_group", methods=['POST'])
@crossdomain(origin='*')
@auth_token_required
def create_friends_group():

    user = current_user._get_current_object()
    form = request.get_json()      
    schema = {
                'name':{'type':'string','empty':False},
            }
    v = Validator(schema)   
    if v.validate(form) is False:
        return api_validation_error(v.errors)  

    #first see if this name exists
    group = FriendsGroup.query.filter(and_(FriendsGroup.user_id == user.id,FriendsGroup.name == form['name'])).first()

    if group:
        return api_error("This group name already exists")

    group = FriendsGroup(user_id=user.id,name=form['name'])
    meeple.db.session.add(group)
    meeple.db.session.commit()

    return api_package(data=group.as_dict())