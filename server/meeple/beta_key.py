import meeple
import hashlib
import time
import urllib
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Boolean, DateTime, String, ForeignKey
from werkzeug import generate_password_hash
from user import User

class BetaKey(meeple.db.Model):
    __tablename__ = 'betakey'
    id = Column(Integer,primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('user.user_id'))
    key = Column(String(255))