"""
Player Module
"""

import copy
import datetime
import json
import logging
import random
import uuid

import names
import bson

from .. import DatabaseConnection
MongoDb = DatabaseConnection()


class Player(object):
    """TTT Player"""

    def __init__(self, state=None):
        state = state or {}
        if not state.get('pid'):
            state['pid'] = uuid.uuid4().hex
        if not state.get('name'):
            state['name'] = names.get_first_name()
        if not state.get('color'):
            state['color'] = random.choice(['Blue', 'Red'])
        if not state.get('twitter_creds'):
            state['twitter_creds'] = False
        if not state.get('score'):
            state['score'] = 0
        if not state.get('moves_made'):
            state['moves_made'] = 0
        if not state.get('games_participated_in'):
            state['games_participated_in'] = 0
        state['last_loaded'] = datetime.datetime.utcnow() 
        self.state = state

    @classmethod
    def new(cls, color):
        """Create new player"""
        player = cls({'color': color})
        logging.debug('Created {}'.format(player))
        return player

    @classmethod
    def load(cls, pid, twitter_name=None):
        """Load player state from database"""
        if twitter_name:
            search = {'name': twitter_name, 'twitter_creds': True}
        else:
            search = {'pid': pid}

        state = MongoDb.player.find_one(search)
        if not state:
            raise KeyError('Could not load pid {} from database'.format(pid))
        player = cls(state)
        logging.debug('Loaded {}'.format(player))
        return player

    def save(self):
        """Save player state to database"""
        MongoDb.player.update_one({'pid': self.pid},
                                  {'$set': self.dumpd()}, upsert=True)
        logging.debug('Saved {}'.format(self.__str__()))

    def dumpd(self):
        """Return state as a dict"""
        return self.state

    @classmethod
    def loadd(cls, state):
        """Load player from dict"""
        return cls(state)

    def dumps(self):
        """Return state as a JSON string"""
        return json.dumps(self.state, default=bson.json_util.default)

    @classmethod
    def loads(cls, json_str):
        """Load player from JSON string"""
        return cls(json.loads(json_str, object_hook=bson.json_util.object_hook))

    def __str__(self):
        return 'Player:{} {} {} {} ({}:{}:{}) {}'.format(
            self.pid,
            self.color,
            self.name,
            'Twit' if self.twitter_creds else 'Anon',
            self.score,
            self.moves_made,
            self.games_participated_in,
            self.last_loaded)

    def __eq__(self, other):
        return self.pid == other.pid

    @property
    def pid(self):
        return self.state['pid']
    
    @property
    def color(self):
        return self.state['color']

    @property
    def name(self):
        return self.state['name']

    @name.setter
    def name(self, value):
        self.state['name'] = value

    @property
    def twitter_creds(self):
        return self.state['twitter_creds']

    @twitter_creds.setter
    def twitter_creds(self, value):
        self.state['twitter_creds'] = value

    @property
    def score(self):
        return self.state['score']

    @score.setter
    def score(self, value):
        self.state['score'] = value

    @property
    def moves_made(self):
        return self.state['moves_made']

    @moves_made.setter
    def moves_made(self, value):
        self.state['moves_made'] = value

    @property
    def games_participated_in(self):
        return self.state['games_participated_in']

    @games_participated_in.setter
    def games_participated_in(self, value):
        self.state['games_participated_in'] = value

    @property
    def last_loaded(self):
        return self.state['last_loaded']

    def get_move(self):
        """Return move from player"""
        raise NotImplementedError

