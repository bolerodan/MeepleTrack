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
    args = request.args
    user = current_user._get_current_object()
    if 'NoGroup' in args:
        #Lets get friends that are NOT in groups only        
        q = Friends.query.filter(and_(Friends.user_id == user.id,Friends.group_id == None)).all()  
    else:        
        #otherwise lets get ALL friends regardless if they are in a group or not
        q = Friends.query.filter(Friends.user_id == user.id).all()    
    friends = []
    for f in q:
        friends.append(f.as_dict())

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
    non_grouped = []

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


@meeple.api.route('/friends/groups/<id>', endpoint="add_friend_to_group", methods=['POST'])
@crossdomain(origin='*')
@auth_token_required
def add_friend_to_group(id):
    user = current_user._get_current_object()  
    form = request.get_json()
    schema = {
                'id':{'type':'integer','empty':False},
            } 
    v = Validator(schema)   
    if v.validate(form) is False:
        return api_validation_error(v.errors)  
    #first see if this is a valid group
    group = FriendsGroup.query.filter(and_(FriendsGroup.user_id == user.id,FriendsGroup.id == id)).first()

    if group:
        #lets see if this is a confirmed friend of yours
        friend = Friend.query.filter(and_(Friend.user_id == user.id,Friend.friend_id == form['id'],Friend.confirmed == True)).first()
        if friend:
            #lets see if this friend is not in this group
            if friend.group_id == group.id:
                return api_error("This friend is already in this group")
            else:
                friend.group_id = group.id
                meeple.db.session.commit()
                return api_package()
        else:
            return api_error("Friend does not exist")
    else:
        return api_error("This group does not exist.")



