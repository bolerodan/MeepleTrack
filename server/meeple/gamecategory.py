import meeple
from sqlalchemy.orm import relationship
from sqlalchemy import Column,Integer,String

class GameCategory(meeple.db.Model):

    __tablename__ = 'gamecategory'
    gamecategory_id = Column(Integer, primary_key=True)      
    name = Column(String(255))
    def as_dict(self):
        result = {}
        result['name'] = self.name
        result['gamecategory_id'] = self.gamecategory_id
        return result