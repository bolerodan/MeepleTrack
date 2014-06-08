import meeple
import hashlib
import time
import urllib
from sqlalchemy.orm import aliased, relationship
from sqlalchemy import Column, Integer, Boolean, DateTime, String, ForeignKey, or_, and_
from werkzeug import generate_password_hash, check_password_hash
from datetime import datetime
from settings import secret_key
from api_tools import date_format
from meeple_exceptions import AchievementNotFound
from meeple.achievements import Achievement

class UserAchievement(meeple.db.Model):
    __tablename__ = 'user_achievement'
    user_id = Column('user_id', Integer, ForeignKey('user.user_id'),primary_key=True)
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


class User(meeple.db.Model):

    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    user_string_id = Column(String(32))
    email = Column(String(60), nullable=False)
    pwdhash = Column(String())
    surname = Column(String(255))
    givennames = Column(String(255))
    created = Column(DateTime, default=datetime.utcnow())
    achievements = relationship(UserAchievement)
    last_access = Column(DateTime)
    role = Column(String(32), default="User") #this probably should be some sorta ENUM

    def __init__(self, email, givennames, lastname):
        self.email = email.lower()
        self.givennames = givennames.strip()
        self.surname = lastname.strip()

    @classmethod
    def authquery(cls):
        from authentication import authenticated_user
        user = authenticated_user()

        if type(user) is type(""):
            return cls.query.filter(User.user_id == -1)  # Impossible user will return empty list

        if user.role == 'Developer':  # pragma: no cover
            return cls.query
        q = cls.query    
        q = q.filter(cls.user_id == user.user_id)
        return q

    def add_achievement(self,achievement_id):
        #now we check if we have this achievement.
        user_achievement = UserAchievement.query.filter(UserAchievement.achievement_id == achievement_id,
                                                        UserAchievement.user_id == self.user_id).first()
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

    def generate_string_id(self):
        self.user_string_id = hashlib.md5(str(self.user_id)+self.email+secret_key).hexdigest()

    def change_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def display_name(self):
        return self.givennames + ' ' + self.surname

    def as_minimal_dict(self):
        result = {}
        result['user_id'] = self.user_id
        result['email'] = self.email
        result['givennames'] = self.givennames
        result['lastname'] = self.surname

        return result
    def as_dict(self):

        from api_tools import date_format
        result = {}

        result['user_id'] = self.user_id
        result['email'] = self.email
        result['givennames'] = self.givennames
        result['lastname'] = self.surname
        result['created'] = date_format(self.created)
        result['gravatar_url'] = self.gravatar_url()
        result['authenticatable'] = self.pwdhash is not None        
        result['achievements'] = []
        result['last_access'] = ''
        if self.last_access is not None:
            result['last_access'] = date_format(self.last_access)

        for a in self.achievements:
            result['achievements'].append(a.as_dict())
        return result

    @classmethod
    def from_string_id(cls, userid):
        return cls.query.filter(cls.user_string_id == str(userid)).first()

    @classmethod
    def from_credentials(cls, email, password):

        q = cls.query
        q = q.filter(User.email == email.lower())

        user = q.first()
        if user is not None:
            if user.check_password(password):
                return user
        return None

    def check_password(self, password):

        if self.pwdhash is not None and check_password_hash(self.pwdhash, password):
            self.last_access = datetime.utcnow()
            meeple.db.session.commit()
            return True

        return False

    def activation_key(self):
        return hashlib.sha256(secret_key+self.email+str(self.created)+str(self.pwdhash)).hexdigest()

    def gravatar_url(self):
        return 'https://www.gravatar.com/avatar/' + hashlib.md5(self.email.lower()).hexdigest() + '?'


class UserPasswordReset(meeple.db.Model):

    __tablename__ = 'user_password_reset'
    token = Column(String(64), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    created = Column(DateTime, default=datetime.utcnow())

    def __init__(self, user_id):
        self.user_id = user_id
        self.token = hashlib.sha256(secret_key+str(self.user_id)+str(time.time())).hexdigest()