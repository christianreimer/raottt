"""
Implements the modified Tic Tac Toe game.

Keeps track of the current board state as well as the history of the game,
specifically the set of users that have previousely played this game, and the
change in board value.
"""

import uuid

from ..game import COLORS
from ..game import opponent
from ..util import Color
from .board import Board
from .score import empty_score_tracker
from .score import post_move_score_update
from .score import show_score
from .score import post_game_score_update


class Game(object):
    """Tracks the current state as well as the history of the game."""
    def __init__(self, first_player):
        self.ugid = uuid.uuid4().hex
        self.board = None
        self.teams = {k: set() for k in COLORS}
        self.next_color = first_player
        self.score_tracker = empty_score_tracker(self.ugid)

    @classmethod
    def new(cls, first_player):
        """Returns a new game."""
        game = cls(first_player)
        game.board = Board()
        return game

    @classmethod
    def load(cls, data):
        """Restores (loads) a game from the given state expressed as a dict."""
        game = cls(data['nextPlayer'])
        game.ugid = data['ugid']
        game.board = Board.load(data['board'])
        game.teams = set(data['teams'])
        return game

    def dump(self):
        """Returns the game state as a dict."""
        squares = self.board.dump()
        pos_moves = self.board.available_moves(self.next_color)

        return {'board': squares,
                'teams': list(self.teams),
                'nextPlayer': self.next_color,
                'ugid': self.ugid,
                'offBoard': sum([1 for (s, _) in pos_moves if s < 0]) > 0}

    def make_move(self, player):
        """Obtains a move from the passed in player, and then applies that move
        to the game."""
        color = player.color
        opp_color = opponent(player.color)
        upid = player.upid
        assert color == self.next_color

        move = player.get_move(self.board)
        self.board.make_move(color, move[0], move[1])

        score = self.board.value(color)
        ratio = self.board.value_ratio(color)
        winner = self.board.winner()

        score, self.score_tracker = post_move_score_update(
            self.score_tracker, score, ratio, winner, color, upid)

        player.score += score

        # Update teams to record this user has taken a turn for this color
        self.teams[color].add(upid)
        self.board.age(opp_color)
        self.next_color = opp_color


    def cleanup(self, bench):
        """Called after a game has been won"""
        post_game_score_update(
            opponent(self.next_color), self.score_tracker, bench)


    def show(self):
        """Prints the board (in pretty colorized ASCII :-) to stdout."""
        print('Game: %s' % Color.yellow(self.ugid))
        print('Moves Performed: %s' % Color.yellow(
            self.score_tracker['num_moves']))
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

        show_score(self.score_tracker)
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

        # If we have made 6 or more moves, then there must be 6 pieces
        if self.score_tracker['num_moves'] >= 6:
            assert pieces == 6

        # Check that all pieces have a count between 1 and 5
        pieces = len([p for p in self.board.squares if p.count < 1] +
                     [p for p in self.board.squares if p.count > 5])
        assert not pieces

        # Check that we have at most one piece with a count of 1
        pieces = len([p for p in self.board.squares if p.count == 1])
        assert pieces <= 1

        # Make sure the same upid has not played both sides
        players = set(self.teams['Red']).intersection(
            set(self.teams['Blue']))
        assert not players
