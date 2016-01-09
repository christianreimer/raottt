"""
Implements the modified the Tic Tac Toe board.

The primary differeneces from classic Tic Tac Toe are:
1. The pieces are know as Blue and Red instead of X and O
2. Each player only gets 3 pieces and will have to move an existing piece on
   their fourth move onward
3. The pieces only get to stay in the same position for 5 rounds, after that
   the piece has to be moved. This is done to prevent a user from grabbing the
   center square and keeping it the entire game

The boad is indexed from 0 to 8 and users -1 to indicate a piece that has not
yet been placed on the board.
"""

import collections
import itertools

from ..game import COLORS
from ..game import INFINITY
from ..game import NUM_PIECES_PER_PLAYER
from ..util import Color


SQUARE_VALUE = [3, 2, 3,   # The value of a square is based on the number of
                2, 4, 2,   # winning combinations it is part of
                3, 2, 3]

WINNING_COMBINATIONS = (
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6])

Undo = collections.namedtuple('Undo', ['source', 'target', 'square'])


class Square(object):
    """Implements a single square on the TTT board"""
    def __init__(self, color=None, count=5):
        assert color in COLORS or color is None, \
            "%s is not a valid color for a square" % color
        self.color = color
        self.count = count
        self.empty = color is None

    @classmethod
    def loadd(cls, data):
        """Loads the sqare state from a python dict"""
        return cls(data['color'], data['count'])

    def dumpd(self):
        """Dumps the square state as a python dict"""
        return {'color': self.color, 'count': self.count}

    def __str__(self):
        if self.color:
            return (Color.blue(self.count) if self.color == 'Blue'
                    else Color.red(self.count))
        else:
            return ' '

    def __repr__(self):
        return self.__str__()


class Board(object):
    """Implements the TTT Board"""
    def __init__(self, squares=None):
        self.squares = squares or [Square() for _ in range(9)]
        self.undo_chain = []

    @classmethod
    def loadd(cls, data):
        """Loads the game state from a python dict"""
        game = cls([Square.loadd(s) for s in data])
        return game

    def dumpd(self):
        """Dumps the game state as a python list"""
        return [s.dumpd() for s in self.squares]

    def show(self):
        """Prints the board to stdout"""
        for square in [str(self.squares[i:i + 3]) for i in range(0, 9, 3)]:
            print(square)

    def empty_squares(self):
        """Returns a list of indices corresponding to empty squares"""
        return [i for i, s in enumerate(self.squares) if s.empty]

    def available_moves(self, color):
        """Returns all the available moves for this player as a list of
        (source_index, target_index) tuples. If the player has a piece where
        the count has reached 1, then that will be the only source since it
        must be moved. In addition, if the player has any pieces not on the
        board, then those pieces must be moved. The targets are simply the
        empty board pieces"""
        sources = self.get_squares(color)
        if -1 in sources:
            sources = [-1]
        else:
            for source in sources:
                if self.squares[source].count == 1:
                    # This is the only possible move ..
                    sources = [source]
                    break

        targets = self.empty_squares()
        permutations = [p for p in itertools.product(sources, targets)]
        return permutations

    def available_combinations(self, color):
        """Returns a list of winning combos that are still available"""
        return self.available_moves(color) + self.get_squares(color)

    def blue_won(self):
        """Returns true if the Blue player has won"""
        return self.winner() == 'Blue'

    def red_won(self):
        """Returns true if the Red player has won"""
        return self.winner() == 'Red'

    def winner(self):
        """Returns the winning player or None if the game is still active"""
        for player in COLORS:
            positions = self.get_squares(player)
            for combo in WINNING_COMBINATIONS:
                win = True
                for pos in combo:
                    if pos not in positions:
                        win = False
                if win:
                    return player
        return None

    def get_squares(self, color):
        """Returns a list of indices corresponding to squares occupied by
        the given color. If the color has pieces off the board, then
        index -1 will be added to the list to indicate this"""
        squares = [k for k, v in enumerate(self.squares) if v.color == color]
        squares_off_board = NUM_PIECES_PER_PLAYER - len(squares)
        if squares_off_board:
            squares = squares + [-1] * squares_off_board
        return squares

    def valid_move(self, color, move):
        """Checks that the proposed move is valid, does not update board"""
        return move in self.available_moves(color)

    def make_move(self, color, source, target, count=5):
        """Move a piece belonging to color from source to target"""
        if source >= 0:
            # Negative index is used to indicate pieces off the board, so we
            # only want to wipe out the source square if it is on the board
            self.undo_chain.append(Undo(source, target, self.squares[source]))
            self.squares[source] = Square()
        else:
            self.undo_chain.append(Undo(source, target, Square()))
        self.squares[target] = Square(color=color, count=count)

    def undo_last_move(self):
        """Undo the last move and restore the board to the previous state"""
        if self.undo_chain:
            undo = self.undo_chain.pop()
            self.squares[undo.target] = Square()
            if undo.source != -1:
                # -1 is used as the source for a piece that is off the board,
                # so we only want to override the source square if it has a
                # different value (e.g was on the board)
                self.squares[undo.source] = undo.square

    def value(self, color):
        """Calculates the valus of the board for the specified color. The
        value is based on the occupied squares, the number of turns we can
        remain there and the empty squares. The most valuable empty square is
        not counted, since we assume the opponent will move there.

        If the color has won, then the value is INFINITY, and if the opponent
        has won, then the value is -INFINITY"""
        winner = self.winner()
        if winner and color == winner:
            return INFINITY + 1
        if winner and color != winner:
            return -1 * INFINITY

        occupied_val = sum([SQUARE_VALUE[i] * self.squares[i].count
                            for i in self.get_squares(color) if i >= 0])
        free_squares = [SQUARE_VALUE[i] for i in self.empty_squares()]
        free_squares.sort()
        free_val = sum(free_squares[:-1])
        return occupied_val + free_val

    def value_ratio(self, color):
        """Returns the value of the board expressed as a ratio. The ratio
        returned is specific to the player passed in. If the game has been
        won then the ratio returned will be 0 or 1 depending on the winner."""
        winner = self.winner()
        if winner and color == winner:
            return 1
        if winner and color != winner:
            return 0

        blue_val = self.value('Blue')
        red_val = self.value('Red')
        total_val = blue_val + red_val

        return (red_val / total_val) if color == 'Red' else \
               (blue_val / total_val)

    def age(self, color):
        """Ages the board by one turn for the specified color"""
        for square in self.squares:
            if square.color == color:
                square.count -= 1

    def diff(self, old):
        """Returns the move needed to get to new_state"""
        source = -1
        dest = None
        for i, sqr in enumerate(old.squares):
            if sqr.color and not self.squares[i].color:
                source = i
            if not sqr.color and self.squares[i].color:
                dest = i
        return (source, dest)
