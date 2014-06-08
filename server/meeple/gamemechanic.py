import meeple
from sqlalchemy.orm import relationship
from sqlalchemy import Column,Integer,String

class GameMechanic(meeple.db.Model):

    __tablename__ = 'gamemechanic'
    gamemechanic_id = Column(Integer, primary_key=True)      
    name = Column(String(255))
    def as_dict(self):
        result = {}
        result['name'] = self.name
        result['gamemechanic_id'] = self.gamemechanic_id
        return result