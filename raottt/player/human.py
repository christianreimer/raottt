"""
Human (console) player
"""

from .player import Player


class HumanPlayer(Player):
    """Implementation of Player which reads moves moves from stdin"""

    def __init__(self, data=None):
        super(HumanPlayer, self).__init__(data)

    @classmethod
    def load(cls, player):
        return cls(player.dumpd())

    def __str__(self):
        return 'Human {}'.format(super(HumanPlayer, self).__str__())

    def get_move(self, board):
        """Returns the next move selected by the human player. Overrides
        get_move in the Player class."""

        while True:
            try:
                move = input("Move (source, target): ")
                source = int(move[0])
                target = int(move[1])
            except (ValueError, IndexError):
                source = target = None

            if (source, target) not in board.available_moves(self.color):
                print("Valid moves are: {}".format(
                    board.available_moves(self.color)))
                continue

            return (source, target)

