import meeple
import hashlib
import time
from sqlalchemy.orm import relationship,aliased
from sqlalchemy import  Column, Integer, Boolean, DateTime, String, ForeignKey, or_,and_
from datetime import datetime
from user import User

class FriendsListGroup(meeple.db.Model):
	__tablename__ = 'friends_list_group'
	id = Column(Integer,primary_key=True)
	name = Column(String(100))
	def as_dict():
		r = {}
		r['id'] = self.id
		r['name'] = self.name
		return r

class FriendsList(meeple.db.Model):
	__tablename__ = 'friends_list'
	user_id = Column(Integer, ForeignKey('user.id'),primary_key=True)
	friend_id = Column(Integer, ForeignKey('user.id'),primary_key=True)
	group_id = Column(Integer, ForeignKey('friends_list_group.id'),nullable=True)
	friend = relationship("User",foreign_key=friend_id)
	group = relationship("Achievement",uselist=False)

	def as_dict():
		r = {}
		r['group'] = self.group.as_dict()
		r['friend'] = self.friend.as_dict()
		return r