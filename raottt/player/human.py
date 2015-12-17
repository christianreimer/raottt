"""
Human (console) player
"""

from .player import Player


class HumanPlayer(Player):
    """Implementation of Player which reads moves form stdin and prints to
    stdout"""
    def __init__(self, color, opponent, name=None, upid=None):
        super(HumanPlayer, self).__init__(color, opponent, name, upid)

    def __str__(self):
        """Return string representation of the player"""
        return 'Human: %s' % super(HumanPlayer, self).__str__()

    def dump(self):
        """Dumps the Player state as a python dict"""
        return {'kind': 'Human'}.update(super(HumanPlayer, self).dump())

    def get_move(self, board):
        """Returns the next move selected by the human player. Overrides
        get_move in the Player class."""

        while True:
            move = input("Move (source, target): ")
            try:
                source = int(move.split()[0])
                target = int(move.split()[1])
            except (ValueError, IndexError):
                source = target = None

            if (source, target) not in board.available_moves(self.color):
                print("Valid moves are: {}".format(
                    board.available_moves(self.color)))
                continue

            return (source, target)

