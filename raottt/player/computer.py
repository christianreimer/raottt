"""
Computer (MinMax AI) Player
"""

import random

from .player import Player
from ..game import INFINITY


class ComputerPlayer(Player):
    """Implementation of Player which uses a basic min/max algorithm to pick
    the next move. Looks MAX_HORIZON moves ahead."""

    MAX_HORIZON = 4

    def __init__(self, color, opponent, name=None, upid=None):
        """Initialize a computer player"""
        super(ComputerPlayer, self).__init__(color, opponent, name, upid)

    def get_move(self, board):
        """Returns the next move selected by the computer player. Overrides
        get_move in the Player class."""
        return self.calculate_move(board, self.color)

    def minimize(self, board, color, horizon):
        """Selects the move that will minimize the value for the specified
        color."""
        horizon += 1
        if horizon > self.MAX_HORIZON:
            return -1 * board.value(color)

        winner = board.winner()
        if winner == color:
            return -1 * INFINITY + horizon
        elif winner == self.opponent(color):
            return 1 * INFINITY - horizon

        best_value = INFINITY
        for (source, target) in board.available_moves(color):
            board.make_move(color, source, target)
            value = self.maximize(board, self.opponent(color), horizon) - horizon
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
        elif winner == self.opponent(color):
            return -1 * (INFINITY + horizon)
        # Make sure that initial best_value is worse than the worst possible
        # move which would be to loose, and have a value on -(INFINITY+1)
        best_value = -1 * INFINITY
        for (source, target) in board.available_moves(color):
            board.make_move(color, source, target)
            value = self.minimize(board, self.opponent(color), horizon) + horizon
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
            value = self.minimize(board, self.opponent(color), 0)
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
                min_ = self.minimize(board, self.opponent(color), 1)
                print('Minimize (%s, %s) -> %s' % (source, target, min_))
                board.undo_last_move()
            assert False, "No move found for computer player"
        return random.choice(moves)
