"""
Computer (MinMax AI) Player
"""

import logging
import random

from ..game import INFINITY
from ..game import opponent

from .player import Player


class ComputerPlayer(Player):
    """Implementation of Player which uses a basic min/max algorithm to pick
    the next move. Looks MAX_HORIZON moves ahead."""

    MAX_HORIZON = 4

    def __init__(self, data=None):
        super(ComputerPlayer, self).__init__(data)

    def __str__(self):
        return 'Computer {}'.format(super(ComputerPlayer, self).__str__())

    @classmethod
    def new(cls, color):
        """Create new ComputerPlayer"""
        player = cls({'color': color})
        logging.debug('New {}'.format(player))
        return player

    @classmethod
    def load(cls, player):
        return cls(player.dumpd())

    def get_move(self, board):
        """Returns the next move selected by the computer player. Overrides
        get_move in the Player class."""
        move = self.calculate_move(board, self.color)
        logging.debug('Player {} moved {}'.format(self.pid, move))
        return move

    def minimize(self, board, color, horizon):
        """Selects the move that will minimize the value for the specified
        color."""
        horizon += 1
        if horizon > self.MAX_HORIZON:
            return -1 * board.value(color)

        winner = board.winner()
        if winner == color:
            return -1 * INFINITY + horizon
        elif winner == opponent(color):
            return 1 * INFINITY - horizon

        best_value = INFINITY
        for (source, target) in board.available_moves(color):
            board.make_move(color, source, target)
            value = self.maximize(board, opponent(color), horizon) - horizon
            board.undo_last_move()
            if value < best_value:
                best_value = value
        return best_value

    def maximize(self, board, color, horizon):
        """Selects the move that will maximize the value for the specified
        color"""
        horizon += 1
        if horizon > self.MAX_HORIZON:
            return board.value(color)

        winner = board.winner()
        if winner == color:
            return INFINITY - horizon
        elif winner == opponent(color):
            return -1 * (INFINITY + horizon)
        # Make sure that initial best_value is worse than the worst possible
        # move which would be to loose, and have a value of -(INFINITY+1)
        best_value = -1 * INFINITY
        for (source, target) in board.available_moves(color):
            board.make_move(color, source, target)
            value = self.minimize(board, opponent(color), horizon) + horizon
            board.undo_last_move()
            if value > best_value:
                best_value = value
        return best_value

    def calculate_move(self, board, color):
        """Loops through all available moves and returns the 'best' move,
        which is the move that maximizes the score for the given color."""
        moves = []
        best_value = -2 * INFINITY  # Worse than the worst possible move

        for (source, target) in board.available_moves(color):
            board.make_move(color, source, target)
            value = self.minimize(board, opponent(color), 0)
            board.undo_last_move()
            # print('%s -> %s has value %s' % (source, target, value))
            if value > best_value:
                moves = [(source, target)]
                best_value = value
            elif value == best_value:
                moves.append((source, target))

        if not moves:
            print('****** No Moves *******')
            print('Available Moves: %s' % board.available_moves(color))
            for (source, target) in board.available_moves(color):
                board.make_move(color, source, target)
                min_ = self.minimize(board, opponent(color), 1)
                print('Minimize (%s, %s) -> %s' % (source, target, min_))
                board.undo_last_move()
            assert False, "No move found for computer player"
        return random.choice(moves)
