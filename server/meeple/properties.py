import meeple
import hashlib
import time
from sqlalchemy.orm import relationship
from sqlalchemy import  Column, Integer, Boolean, DateTime, String, ForeignKey, or_ ,Enum
from datetime import datetime
from user import User
from game_session import GameSession


class PropertyDef(meeple.db.Model):
    __tablename__ = 'propdef'
    propdef_id = Column(Integer, primary_key=True)
    name = Column(String(64),nullable=False)
    fieldtype=Column(Enum('string','integer','float',name='fieldtypes'),default='integer')
    creator_id = Column(Integer,ForeignKey("user.id"),nullable=True) #Does NOT need to be linked to a user
    def as_dict(self):
        result = {}
        result["propdef_id"] = self.propdef_id
        result['name'] = self.name
        result['fieldtype'] = self.fieldtype
        result['creator_id'] = self.creator_id

        return result


class Property(meeple.db.Model):
    __table__name = 'property'
    property_id = Column(Integer,primary_key=True)
    propdef_id = Column(Integer,ForeignKey("propdef.propdef_id"),nullable=False)    
    value_string = Column(String(255))
    value_integer = Column(Integer)

    propdef = relationship(PropertyDef)

    def set_value(self, value):
        self.value_string = None
        self.value_integer = None

        if self.propdef.fieldtype == 'string':
            self.value_string = str(value)
            return True
        elif self.propdef.fieldtype == 'integer':
            try:
                self.value_integer = int(value)
                return True
            except ValueError:
                return False
        return False

    def value(self):
        if self.propdef.fieldtype == 'string':
            return self.value_string
        elif self.propdef.fieldtype == 'integer':
            return self.value_integer

    def as_dict(self):
        result = {}

        result["property_id"] = self.property_id
        result["propertydef"] = self.propdef.as_dict()
        result["value"] = self.value()

        return result   
        
class GameSessionProperties(meeple.db.Model):
    __tablename__ = "gamesession_properties"
    id = Column(Integer,primary_key=True)
    gamesession_id = Column(ForeignKey("game_session.id"),nullable=False,primary_key = True)
    player_id = Column(ForeignKey("user.id"),nullable=False,primary_key = True)
    property_id = Column(ForeignKey("property.property_id"),nullable=False,primary_key = True)
    property = relationship("Property")
    gamesession = relationship("GameSession")
    user = relationship("User")

    def as_dict(self):
        result = {}
        result['property'] = self.property.as_dict()
        result['user_id'] = self.player_id

        return result