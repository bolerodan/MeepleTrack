import meeple
import hashlib
import time
from sqlalchemy.orm import relationship,aliased
from sqlalchemy import  Column, Integer, Boolean, DateTime, String, ForeignKey, or_,and_
from datetime import datetime
from user import User
from game import Game


gamesession_players = meeple.db.Table('gamesession_players',
    Column('game_session_id', Integer, ForeignKey('game_session.id')),
    Column('user_id', Integer, ForeignKey('user.id'))
)

class GameSession(meeple.db.Model):

    __tablename__ = 'game_session'
    id = Column(Integer, primary_key=True)

    name = Column(String(255))
    created = Column(DateTime, default=datetime.utcnow())
    start_time = Column(DateTime,default=datetime.utcnow())
    end_time = Column(DateTime)
    # public = Column(Boolean,default=False) #if public, people can share a link and see a detailed card about it.
    game_id = Column(Integer, ForeignKey('game.game_id')) #can only be related to one game
    host_id = Column(Integer, ForeignKey('user.id')) #can only have one host, or creator of this session
    players = relationship(User,secondary=gamesession_players,backref="game_sessions") #can have multiple players
    game = relationship(Game)
    host = relationship(User)


    def as_dict(self):

        from api_tools import date_format
        result = {}
        result['id'] = self.id
        result['name'] = self.name
        result['created'] = date_format(self.created)
        result['start_time'] = date_format(self.start_time)
        result['host'] = self.host.as_minimal_dict()
        result['game'] = self.game.as_search()
        result['properties'] = []
        result['players'] = []
        for user in self.players:
            from properties import GameSessionProperties
            u = user.as_minimal_dict()
            u['properties'] = []
            user_props = GameSessionProperties.query.filter(GameSessionProperties.player_id == user.id).filter(GameSessionProperties.gamesession_id == self.id).all()
            for prop in user_props:
                print "prop: ",prop.as_dict()
                u['properties'].append(prop.as_dict()['property'])

            result['players'].append(u)
        return result    