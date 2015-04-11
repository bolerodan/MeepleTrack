import meeple
import hashlib
import time
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Text, Integer, Boolean, DateTime, String, ForeignKey, or_ 
from datetime import datetime
from publisher import Publisher
from gamecategory import GameCategory
from gamemechanic import GameMechanic

game_publisher = meeple.db.Table('game_publisher',
    Column('game_id', Integer, ForeignKey('game.game_id')),
    Column('publisher_id', Integer, ForeignKey('publisher.publisher_id'))
)

game_gamecategory = meeple.db.Table('game_gamecategory',
    Column('game_id', Integer, ForeignKey('game.game_id')),
    Column('gamecategory_id', Integer, ForeignKey('gamecategory.gamecategory_id'))
)
game_gamemechanic = meeple.db.Table('game_gamemechanic',
    Column('game_id', Integer, ForeignKey('game.game_id')),
    Column('gamemechanic_id', Integer, ForeignKey('gamemechanic.gamemechanic_id'))
)

game_gameexpansion = meeple.db.Table('game_gameexpansion',
    Column('parent_game_id', Integer, ForeignKey('game.game_id')),
    Column('expansion_game_id', Integer, ForeignKey('game.game_id'))
)
class Game(meeple.db.Model):

    __tablename__ = 'game'
    game_id = Column(Integer, primary_key=True)      
    created = Column(DateTime, default=datetime.utcnow())
    name = Column(String(255))
    publisher =  relationship("Publisher",secondary="game_publisher",backref="games") #can have multiple publishers
    game_categories = relationship("GameCategory",secondary="game_gamecategory")
    game_mechanic = relationship("GameMechanic",secondary="game_gamemechanic")
    expansions = relationship("Game",secondary="game_gameexpansion",
                                primaryjoin=game_gameexpansion.c.parent_game_id == game_id,
                                secondaryjoin=game_gameexpansion.c.expansion_game_id == game_id
                            )
    achievements = relationship("Achievement",backref="game") #can have multiple achievements.
    yearpublished = Column(Integer)
    description = Column(Text)    
    minplayers = Column(Integer)
    maxplayers = Column(Integer)
    recommendedplayers  = Column(Integer)
    playingtime =  Column(Integer)
    thumbnail = Column(Text)
    image = Column(Text)


    def addPublisher(self,publisherName):
        """This function shouldnt really be here imo"""
        publisher = Publisher.query.filter(Publisher.name == publisherName).first()
        if publisher:
            self.publisher.append(publisher)
        else:
            publisher = Publisher()
            publisher.name = publisherName
            self.publisher.append(publisher)
            # meeple.db.session.add(publisher)
            # meeple.db.session.commit()

    def addCategory(self,categoryName):

        c = GameCategory.query.filter(GameCategory.name == categoryName).first()
        if c:
            self.game_categories.append(c)
        else:
            gc = GameCategory()
            gc.name = categoryName
            self.game_categories.append(gc)  

    def addMechanic(self,name):

        m = GameMechanic.query.filter(GameMechanic.name == name).first()
        if m:
            self.game_mechanic.append(m)
        else:
            gm = GameMechanic()
            gm.name = name
            self.game_mechanic.append(gm)

    def as_minimal_dict(self):
        result = {}
        result['name'] = self.name
        result['game_id'] = self.game_id
        return result

    def as_search(self):
        result = {}
        result['id'] = self.game_id
        result['name'] = self.name        
        result['image'] = self.image
        result['description'] = (self.description[:200] + '..') if len(self.description) > 200 else self.description
        result['minplayers'] = self.minplayers
        result['maxplayers'] = self.maxplayers   
        result['playingtime'] = self.playingtime
        result['thumbnail'] = self.thumbnail      
        return result  
    def as_dict(self):
        from api_tools import date_format
        result = {}

        result['id'] = self.game_id
        result['created'] = date_format(self.created)
        result['name'] = self.name
        result['description'] =self.description
        result['minplayers'] = self.minplayers
        result['maxplayers'] = self.maxplayers
        result['yearpublished'] = self.yearpublished
        result['recommendedplayers'] = self.recommendedplayers
        result['playingtime'] = self.playingtime
        result['image'] = self.image
        result['thumbnail'] = self.thumbnail
        result['achievements'] = []
        result['publishers'] = []
        result['gamecategories'] = []
        result['gamemechanic'] = []
        result['expansions'] = []
        for a in self.achievements:
            result['achievements'].append(a.as_dict())
        for p in self.publisher:
            result['publishers'].append(p.as_dict())
        for gc in self.game_categories:
            result['gamecategories'].append(gc.as_dict())
        for gm in self.game_mechanic:
            result['gamemechanic'].append(gm.as_dict())
        for e in self.expansions:
            result['expansions'].append(e.as_minimal_dict())
        return result
