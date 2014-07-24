import meeple
import hashlib
import time
import urllib
from flask.ext.security import UserMixin
from sqlalchemy.orm import aliased, relationship, backref
from sqlalchemy import Column, Integer, Boolean, DateTime, String, ForeignKey, or_, and_
from werkzeug import generate_password_hash, check_password_hash
from datetime import datetime
from settings import secret_key
from api_tools import date_format
from meeple_exceptions import AchievementNotFound
from meeple.achievements import Achievement
from meeple.roles import Role, roles_users

class UserAchievement(meeple.db.Model):
    __tablename__ = 'user_achievement'
    user_id = Column('user_id', Integer, ForeignKey('user.id'),primary_key=True)
    achievement_id = Column('achievement_id', Integer, ForeignKey('achievement.achievement_id'),primary_key=True)
    date_unlocked = Column(DateTime)
    progress =  Column('progress',Integer,default=1)
    achievement = relationship("Achievement",uselist=False)

    def as_dict(self):
        result = {}
        result['progress'] = self.progress
        result['date_unlocked'] = date_format(self.date_unlocked)
        result['achievement'] = self.achievement.as_dict()
        return result


class User(meeple.db.Model,UserMixin):

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(60), nullable=False)
    password = Column(String(255))
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    last_login_at = Column(DateTime())
    created = Column(DateTime, default=datetime.utcnow())
    current_login_at = Column(DateTime())
    firstname = Column(String(100))
    lastname = Column(String(100))
    login_count = Column(Integer)
    current_login_ip = Column(String(11))
    last_login_ip = Column(String(11))
    achievements = relationship(UserAchievement)
    roles = relationship('Role', secondary=roles_users,
                            backref=backref('users', lazy='dynamic'))


    def display_name(self):
        return self.firstname + " " + self.lastname
        
    def add_achievement(self,achievement_id):
        #now we check if we have this achievement.
        user_achievement = UserAchievement.query.filter(UserAchievement.achievement_id == achievement_id,
                                                        UserAchievement.user_id == self.id).first()
        if user_achievement is not None:            
            max_progress = user_achievement.achievement.max_progress
            """
                we already have this achievement but now we need to check
                if we can increment the progress of this achievement by its
                max_progress
            """
            if max_progress > 1 and user_achievement.progress < max_progress:
                user_achievement.progress += 1

                if max_progress == user_achievement.progress: #lets check if we got this achievement
                    user_achievement.date_unlocked = datetime.utcnow()
        else:
            """
                Otherwise we do not have this achievement
                so lets mark it down as real
            """
            achievement = Achievement.query.filter(Achievement.achievement_id == achievement_id).first()
            if achievement is not None:
                user_achievement = UserAchievement()
                user_achievement.achievement = achievement
                """
                    If this achievement has a progress of 1, you
                    only need to get this once to unlock it
                """
                if achievement.max_progress == 1:
                    user_achievement.date_unlocked = datetime.utcnow() #we got this achievement now.
                self.achievements.append(user_achievement)
            else:
                raise AchievementNotFound("Unknown Achievement to add to user")




    def display_name(self):
        return self.firstname + ' ' + self.lastname

    def as_minimal_dict(self):
        result = {}
        result['id'] = self.id
        result['email'] = self.email
        result['givennames'] = self.firstname
        result['lastname'] = self.lastname
        result['display_name'] = self.display_name()

        return result
    def as_dict(self):

        from api_tools import date_format
        result = {}

        result['id'] = self.id
        result['email'] = self.email
        result['givennames'] = self.firstname
        result['lastname'] = self.lastname
        result['display_name'] = self.display_name()
        result['created'] = date_format(self.created)
        result['gravatar_url'] = self.gravatar_url()     
        result['achievements'] = []
        result['last_access'] = ''
        if self.last_login_at is not None:
            result['last_access'] = date_format(self.last_login_at)

        for a in self.achievements:
            result['achievements'].append(a.as_dict())
        return result


    def activation_key(self):
        return hashlib.sha256(secret_key+self.email+str(self.created)+str(self.pwdhash)).hexdigest()

    def gravatar_url(self):
        return 'https://www.gravatar.com/avatar/' + hashlib.md5(self.email.lower()).hexdigest() + '?'


class UserPasswordReset(meeple.db.Model):

    __tablename__ = 'user_password_reset'
    token = Column(String(64), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    created = Column(DateTime, default=datetime.utcnow())

    def __init__(self, user_id):
        self.user_id = user_id
        self.token = hashlib.sha256(secret_key+str(self.user_id)+str(time.time())).hexdigest()