"""
Player - Implments Human and AI Modified TTT Player interfaces

The HumanPlayer reads commands from stdin.
The ComputerPlayer uses a basic min/max algo to select the next move.
"""

import uuid

import names
import timydb

from ..util import Color
from ..game import opponent


class Bench(object):
    """Implements the player bench which is used to track all know players"""
    def __init__(self):
        # self.db = tinydb.TinyDB('bench.db')
        self.players = {}

    def __getitem__(self, upid):
        query = tinydb.Query()
        # return db.search(query.upid == upid)
        return self.players.get(upid, None)

    def register(self, player):
        """Register a new player"""
        self.players[player.upid] = player


class Player(object):
    """Implementation of a TTT Player interface. Specific implementation are
    done in other classes."""
    def __init__(self, color, opp=opponent, name=None, upid=None, score=0):
        self.color = color
        self.opponent = opp
        self.name = name or names.get_first_name()
        self.upid = upid or uuid.uuid4().hex
        self.score = score

    @classmethod
    def load(cls, data):
        """Loads the Player state from a python dict"""
        return cls(color=data['color'], upid=data['upid'], score=data['score'])

    def __str__(self):
        """Return string representation of the player"""
        return '%s %s' % (self.name, Color.me(self.color, self.upid))

    def dump(self):
        """Dumps the Player state as a python dict"""
        return {'color': self.color, 'upid': self.upid, 'score': self.score}

    def get_move(self, board):
        """Returns the user's move"""
        raise NotImplementedError
