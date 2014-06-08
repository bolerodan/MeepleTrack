import meeple
import hashlib
import time
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Text, Integer, Boolean, DateTime, String, ForeignKey, or_ 
from datetime import datetime
from publisher import Publisher


class Achievement(meeple.db.Model):

    __tablename__ = 'achievement'
    achievement_id = Column(Integer, primary_key=True) 
    name = Column(String(255))
    max_progress = Column(Integer,default=1)
    description = Column(Text)
    #xp = Column(Integer)
    game_id = Column(Integer,ForeignKey('game.game_id')) #an achievement can only be related to one specific game.
    thumbnail = Column(Text)

    def as_dict(self):
        result = {}
        result['achievement_id'] = self.achievement_id
        result['name'] = self.name
        result['description'] = self.description
        #result['xp'] = self.xp
        return result