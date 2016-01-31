"""
Implements the modified Tic Tac Toe game.

Keeps track of the current board state as well as the history of the game,
specifically the set of users that have previousely played this game, and the
change in board value.
"""

import datetime
import uuid
import random
import logging

from ..game import COLORS
from ..game import opponent
from ..util import Color
from .board import Board
from .score import Score    

from .. import DatabaseConnection
MongoDb = DatabaseConnection()


class Game(object):
    """Tracks the current state as well as the history of the game."""
    def __init__(self, gid, next_color, board, score, inplay, checkout, player):
        self.gid = gid
        self.next_color = next_color
        self.board = board
        self.score = score
        self.inplay = inplay
        self.checkout = checkout
        self.player = player

    def __str__(self):
        return 'Game:{} next:{} inplay:{} checkout:{}'.format(
            self.gid, self.next_color, self.inplay, self.checkout)

    @classmethod
    def new(cls, first_player):
        """Create a new game"""
        gid = uuid.uuid4().hex
        next_color = first_player
        board = Board()
        score = Score.new(gid)
        game = cls(gid, next_color, board, score, False, None, None)
        logging.debug('New {}'.format(game))
        return game

    @classmethod
    def load(cls, gid, validate=False, player=None):
        """Load the game with specified id from the database"""
        game = cls.loadd(MongoDb.game.find_one({'gid': gid}))

        if not game:
            raise KeyError('gid {} not found in database'.format(gid))

        if validate:
            game_pid = game.player

            if not game_pid == player.pid:
                err_msg = 'Player {} does not have game {} reserved'.format(
                    player.pid, gid)
                logging.error(err_msg)
                raise ValueError(err_msg)

            if not game.inplay:
                err_msg = ('Player {} tried to load game {} which is '
                           'not checked out'.format(player.pid, gid))
                logging.error(err_msg)
                raise ValueError(err_msg)

        logging.debug('Loaded {}'.format(game))
        return game

    def save(self):
        """Save game state to database"""
        MongoDb.game.update_one({'gid': self.gid},
                                {'$set': self.dumpd()}, upsert=True)
        logging.debug('Saved {}'.format(self.__str__()))

    def delete(self):
        """Delete game from database"""
        MongoDb.game.delete_one({'gid': self.gid})
        logging.debug('Deleted {}'.format(self.__str__()))

    @classmethod
    def pick(cls, player, create_if_needed=True):
        """Picks an existing game that can be played by the specified player.
        If no suitable game is found, a new one will be created and returned."""
        gid_lst = [record['gid'] for record in \
            MongoDb.game.find({'next_color': player.color, 'inplay': False})]

        logging.debug('{} can pick from {} possibilities'.format(
            player.color, len(gid_lst)))

        if len(gid_lst) < 5 and create_if_needed:
            gid_lst += create_new_games(5 - len(gid_lst), player.color)

        try:
            gid = random.choice(gid_lst)
        except IndexError:
            raise IndexError('No games ready to play for color {}'.format(
                player.color))

        utc_now = datetime.datetime.utcnow()

        game = cls.loadd(MongoDb.game.find_and_modify(
            query={'gid': gid}, update={'$set':{'inplay': True,
                                                'checkout': utc_now,
                                                'player': player.pid}}))

        logging.debug('Picked {} for pid {}'.format(game, player.pid))
        return game

    @classmethod
    def loadd(cls, state):
        """Restore game state from a dict"""
        gid = state['gid']
        next_color = state['next_color']
        board = Board.loadd(state['board'])
        score = Score.loadd(state['score'])
        inplay = state['inplay']
        checkout = state['checkout']
        player = state['player']
        return cls(gid, next_color, board, score, inplay, checkout, player)

    def dumpd(self):
        """Dump game state as a dict"""
        return {'gid': self.gid,
                'next_color': self.next_color,
                'board': self.board.dumpd(),
                'score': self.score.dumpd(),
                'inplay': self.inplay,
                'checkout': self.checkout,
                'player': self.player}

    def dumpjs(self):
        """Return game state as dict suitable for js"""
        # TODO: Move to adapter
        squares = self.board.dumpd()
        pos_moves = self.board.available_moves(self.next_color)

        return {'board': squares,
                'nextPlayer': self.next_color,
                'ugid': self.gid,
                'offBoard': sum([1 for (s, _) in pos_moves if s < 0]) > 0}
   
    def make_move(self, player):
        """Obtain a move from the passed in player, and then applies that move
        to the game."""
        color = player.color
        opp_color = opponent(player.color)
        pid = player.pid
        assert color == self.next_color

        move = player.get_move(self.board)
        self.board.make_move(color, move[0], move[1])

        score = self.board.value(color)
        ratio = self.board.value_ratio(color)
        winner = self.board.winner()

        score_change = self.score.after_move(score, ratio, winner, color, pid)
        if self.score.moves_made_by_player(player) == 1:
            player.games_participated_in += 1

        # Update teams to record this user has taken a turn for this color
        self.board.age(opp_color)
        self.next_color = opp_color

        # Update global scores to record the move was made
        Score.update_global_score(color, winner == color)

        if winner:
            logging.info('Game {} won by {} pid {}'.format(
                self.gid, player.color, player.pid))

        return score_change

    def cleanup(self, winner):
        """Called after a game has been won"""
        _ = self.score.post_game(winner)
        logging.debug('Game cleanup {}'.format(self.__str__()))
        self.delete()

    def show(self):
        """Prints the board (in pretty colorized ASCII :-) to stdout."""
        print('Game: %s' % Color.yellow(self.gid))
        print('Board Value: %s/%s' % (Color.blue(self.board.value('Blue')),
                                      Color.red(self.board.value('Red'))))
        print('Next Player: %s' % (Color.me(self.next_color,
                                            self.next_color)))

        print('Value Ratio (%s): %s' % (
            Color.me(self.next_color, self.next_color),
            Color.yellow(self.board.value_ratio(self.next_color))))

        print('Value Ratio (%s): %s' % (
            Color.me(opponent(self.next_color),
                     opponent(self.next_color)),
            Color.yellow(self.board.value_ratio(
                opponent(self.next_color)))))

        print(self.score)
        self.board.show()

    def game_over(self):
        """Returns the winner if the game is in a winning (won?) state, or
        None if the game is still in play."""
        return self.board.winner()

    def validate(self):
        """Checks to make sure the game is in a valid state."""
        # Check that we have no more than 6 pieces on the board
        pieces = len([p for p in self.board.squares if p.color])
        assert pieces <= 6

        # Check that all pieces have a count between 1 and 5
        pieces = len([p for p in self.board.squares if p.count < 1] +
                     [p for p in self.board.squares if p.count > 5])
        assert not pieces

        # Check that we have at most one piece with a count of 1
        pieces = len([p for p in self.board.squares if p.count == 1])
        assert pieces <= 1


def create_new_games(num_games, color):
    """Create `num_games` new games that `color` can play"""
    game_lst = []
    for _ in range(num_games):
        game = Game.new(color)
        game.save()
        game_lst.append(game.gid)
    return game_lst

