import meeple
import datetime
import urllib2
from flask import request
from api_tools import api_package, api_error, api_error_missing, api_not_found, verify_email
from flask.ext.security import auth_token_required,current_user
from crossdomain import crossdomain
from user import User
from friends import Friends,FriendsGroup


@meeple.api.route('/friends', endpoint="friends", methods=['GET'])
@crossdomain(origin='*')
@auth_token_required
def friends():
	user = current_user._get_current_object()
	q = Friends.query.filter_by(Friends.user_id == user.id).all()
	friends = []
	for f in q:
		friends.append(f.friend.as_minimal_dict())

	return api_package(data=friends)


@meeple.api.route('/friends/groups', endpoint="friend_groups", methods=['GET'])
@crossdomain(origin='*')
@auth_token_required
def friend_groups():
	user = current_user._get_current_object()
	q = FriendsGroup.query.filter_by(Friends.user_id == user.id).all()
	groups = []
	for g in q:
		friends.append(g.group.as_dict())

	return api_package(data=friends)