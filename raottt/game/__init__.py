"""
Game module
"""

from .. import DatabaseConnection
MongoDb = DatabaseConnection()


COLORS = ('Blue', 'Red')
INFINITY = 999999
NUM_PIECES_PER_PLAYER = 3


def opponent(color):
    """Return the opponent to the color passed in"""
    return COLORS[0] if color == COLORS[1] else COLORS[1]
