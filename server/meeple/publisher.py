import meeple
from sqlalchemy.orm import relationship
from sqlalchemy import Column,Integer,String

class Publisher(meeple.db.Model):

    __tablename__ = 'publisher'
    publisher_id = Column(Integer, primary_key=True)      
    name = Column(String(255))
    def as_dict(self):
        result = {}
        result['name'] = self.name
        result['publisher_id'] = self.publisher_id
        return result