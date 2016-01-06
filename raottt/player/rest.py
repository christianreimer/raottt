"""
REST (Swift App) player
"""


from .player import Player


class RESTPlayer(Player):
    """Implementation of Player which gets moves moves from a REST Api"""

    def __init__(self, state):
        super(RESTPlayer, self).__init__(state)
        self.move = None

    def queue_move(self, move):
        """Set the move in the user so that if can be pulled out again using
        get_move"""
        self.move = move

    def get_move(self, dummy):
        """Returns the move that was queued"""
        return self.move
