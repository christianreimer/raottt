"""
Game module
"""


COLORS = ('Blue', 'Red')
INFINITY = 999999
NUM_PIECES_PER_PLAYER = 3


def opponent(color):
    """Return the opponent to the color passed in"""
    return 'Blue' if color == 'Red' else 'Red'

