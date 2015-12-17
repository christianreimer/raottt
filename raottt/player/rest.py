"""
REST (Swift App) player
"""


from .player import Player


class RESTPlayer(Player):
    """Implements a REST player

    GET raott/game      returns a new game
    PUT raott/move      submit a move
    GET raott/player    returns a player's stats
    """
    def __init__(self, color, opponent, name=None, upid=None):
        """Initializes the RESTPlayer"""
        super(RESTPlayer, self).__init__(color, opponent, name, upid)
        self.move = None

    def queue_move(self, move):
        """Set the move in the user so that if can be pulled out again using
        get_move"""
        self.move = move

    def get_move(self, board):
        """Returns the move that was queued"""
        return self.move
