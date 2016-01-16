"""
Implments the rules to calculate how much to update the user's score by after
a move.

+1 for every move
+2 if move improved the value of the board for your color
+2 if you change from being behind to ahead
+2 if a chain you helped with wins  (??)
+5 if you make the winning move

-4 if the game is lost on the next move
-1 if a chain you helped with looses
-1 if you lower the value of the board
-1 if you change from being ahead to behind

The Game object should keep a tuple of the previous person to make a move
(Player, Score, Ratio) then we can compare in the post_move_score_update if the
current move (that has just completed) improved or worsened things.

Also, if the game ends at this point then we can modify the score of the
previous person who made it happen ...

Questions:
Shoulds we keep track of ALL the people who have participated in the
game (and the number of turns they took - and possibly the ration of imprcements
and decreases??)? That way, when a game ends, we can allocation a number of
point to the winning team (the older the game the more points) and hand them out
to the people who partiipated ...

How should I be notifying you about a score change that happened becuse of a
subsequent move?? Go all out and do smily and frowney faces? "BigGorillaMonkey
just won a game where you made the previous move .. Oh shame on you ..." or
"Great News! BigGorillaMonkey just made the winning move for team Red in a
game that you helped. He was standing on the shoulders of giants. Yours
Shoulders (among others). Great stuff. Have +X points"
"""


import collections
import json
import logging
import math

from ..game import opponent

from .. import DatabaseConnection
MongoDb = DatabaseConnection()


Move = collections.namedtuple('Move', 'pid score ratio')

# +1 for every move
# +1 if move improved the value of the board for your color
# -1 if you lower the value of the board for your color
# +2 if you change your color from being behind to ahead
# -1 if you change your color from being ahead to behind
# +5 if you make the winning move
# -3 if you make the last move before the game is lost


VALUE_MOVE = 1
VALUE_INCREASE_SCORE = 1
VALUE_LOWER_SCORE = -1
VALUE_BEHIND_TO_AHEAD = 2
VALUE_AHEAD_TO_BEHIND = -1
VALUE_WINNING_MOVE = 5
VALUE_LOOSING_MOVE = -3
FACTOR_WIN = 2
FACTOR_LOSS = -1

class Score(object):
    """docstring for Score"""
    def __init__(self, state):
        self.state = state
        self.enqueue_work_f = None

    @classmethod
    def new(cls, gid):
        state = {'gid': gid,
                 'teams': {'Red': collections.defaultdict(int),
                           'Blue': collections.defaultdict(int)},
                 'previous': {'Red': Move(0, 0, 0.50),
                              'Blue': Move(0, 0, 0.50)},
                 'value': 0}
        return cls(state)

    @classmethod
    def loadd(cls, state):
        """Load score state from a dict"""
        return cls(state)

    def dumpd(self):
        """Dump score state as a dict"""
        return self.state

    @classmethod
    def loads(cls, json_str):
        """Load score state from a JSON string"""
        return cls(json.loads(json_str))

    def dumps(self):
        """Dump score state as a JSON string"""
        return json.dumps(self.state)

    @property
    def gid(self):
        return self.state['gid']

    @property
    def teams(self):
        return self.state['teams']

    @teams.setter
    def teams(self, value):
        self.state['teams'] = value

    @property
    def previous(self):
        return self.state['previous']

    @previous.setter
    def previous(self, value):
        self.state['previous'] = value

    @property
    def value(self):
        return self.state['value']

    @value.setter
    def value(self, value):
        self.state['value'] = value

    def after_move(self, score, ratio, winner, color, pid):
        """Update the score and state tracking after a move"""
        a, b, c = self.state['previous'][color]
        prev_move = Move(a, b, c)

        # Record the fact that this pid participated in the game
        self.state['teams'][color][pid] = \
            self.state['teams'][color].get(pid, 0) + 1
        self.state['previous'][color] = Move(pid, score, ratio)

        score_change = VALUE_MOVE

        if score > prev_move.score:
            score_change += VALUE_INCREASE_SCORE
        elif score < prev_move.score:
            score_change += VALUE_LOWER_SCORE

        if prev_move.ratio < 0.50 and ratio > 0.50:
            score_change += VALUE_BEHIND_TO_AHEAD
        elif prev_move.ratio > 0.50 and ratio < 0.50:
            score_change += VALUE_AHEAD_TO_BEHIND

        self.state['value'] += abs(score_change)

        if winner == color:
            one_third_of_value = math.ceil(1/3 * self.state['value'])
            score_change += max(one_third_of_value, VALUE_WINNING_MOVE)
            self.state['value'] -= score_change
        
        logging.debug('Score after_move change {}'.format(score_change))
        return score_change

    def __str__(self):
        return '\n'.join(['Game: {}'.format(self.state['gid']),
                          'Value: {}'.format(self.state['value']),
                          'Team Red: {} players'.format(
                                len(self.state['teams']['Red'])),
                          'Team Blue: {} players'.format(
                                len(self.state['teams']['Blue']))])

    def post_game(self, winning_color, update_db=True):
        """Updates scores as a result of a game being won.

        The idea is that all the players (pids) that participated in the game
        share in the glory (or shame) of the outcome. The total value of the
        game is dependent on the moves that were taken, and each player gets a
        part of the points proportionate to the number of moves that player
        made."""

        points = self.state['value']
        score_lst = []

        team_size = len(self.state['teams'][winning_color])
        for pid, moves in self.state['teams'][winning_color].items():
            score_change = FACTOR_WIN * math.ceil(points/team_size) * moves
            score_lst.append((pid, score_change))

        team_size = len(self.state['teams'][opponent(winning_color)])
        for pid, moves in self.state['teams'][opponent(winning_color)].items():
            score_change = FACTOR_LOSS * math.ceil(points/team_size) * moves
            score_lst.append((pid, score_change))

        logging.debug('Score post_game result {}'.format(
            [(p, d) for (p, d) in score_lst]))

        if update_db:
            MongoDb.updates.insert_many(
                [{'pid': p, 'delta': d} for (p, d) in score_lst])

        return score_lst

    def moves_made_by_player(self, player):
        """Return the number of moves player has made in this game"""
        return self.teams[player.color].get(player.pid, 0)

    @classmethod
    def check_for_score_upate(cls, pid):
        """Check if there are score updates waiting to be applied
        for this player"""
        delta = sum([r['delta'] for r in MongoDb.updates.find({'pid': pid})]) 
        MongoDb.updates.delete_many({'pid': pid})
        logging.info('Player {} had a score change of {} waiting'.format(
            pid, delta))
        return delta

    @classmethod
    def update_global_score(cls, color, won):
        """Update the global scores"""
        logging.debug('Update global score color {} won {}'.format(color, won))
        MongoDb.score.update_one({'color': color},
                                 {'$inc': {'turns': 1,
                                           'wins': won and 1 or 0}})

    @classmethod
    def get_global_score(cls):
        """Return the global score"""
        score_lst = [score for score in MongoDb.score.find()]
        return score_lst

