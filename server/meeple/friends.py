import meeple
import hashlib
import time
from sqlalchemy.orm import relationship,aliased
from sqlalchemy import  Column, Integer, Boolean, DateTime, String, ForeignKey, or_,and_
from datetime import datetime


class FriendRequests(meeple.db.Model):
    __tablename__ = "friend_requests"
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey("user.id"),primary_key=True)
    friend_id = Column(Integer,ForeignKey("user.id"),primary_key=True) #who is my friend
    friend = relationship("User",foreign_keys=friend_id)



class Friends(meeple.db.Model):
    __tablename__ = "friends"
    user_id = Column(Integer,primary_key=True) #whos friend we are looking for.
    friend_id = Column(Integer,ForeignKey("user.id"),primary_key=True) #who is my friend
    group_id = Column(Integer,ForeignKey('friends_group.id'),nullable=True) #does not require a group (default all)
    confirmed = Column(Boolean,default=False) #has the friend_id confirmed this request?
    friend = relationship("User",foreign_keys=friend_id)
    group = relationship("FriendsGroup",foreign_keys=group_id)

    def as_dict(self,group=False):
        r = self.friend.as_minimal_dict()
        if group:
            r['group'] = self.group.as_dict(friends=False)
        return r

class FriendsGroup(meeple.db.Model):
    __tablename__ = "friends_group"
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey('user.id')) 
    name = Column(String(200))
    friends = relationship("User",secondary="friends")      

    def as_dict(self,friends=True):
        r = {}
        r['name'] = self.name
        r['id'] = self.id
        r['friends'] = []
        if friends:
            for friend in self.friends:
                r['friends'].append(friend.as_minimal_dict())

        return r