"""
Random Acts Of Tic Tac Toe

A modified version of Tic Tac Toe (Noughts and Crosses, Xs and Os) where each
player only gets 3 pieces. Once a player has placed all pieces on the board,
subsequent moves are made by moving a piece to an empty spot. Thus, the game
continues on and could -- in theory -- go on forever.

As an added twist, each piece can only remain in the same spot for 5 rounds.
Once the time is up the player is forces to move that piece. This ensure a
player does not occupy the center spot for the entire game, and adds another
dimension for the player to consider.

Finally, a player is expected to participate in many simultanious games against
many different players. Essentially, each turn will be taken in the context of
a different game. When a game is won or lost, all the players who have taken 
part of tht game will reveice a score update.
"""

__author__ = "Christian Reimer"
__version__ = "0.0.1"


from .util import logger
logger.setup()

from .util.database import DatabaseConnection
from .game.game import Game
from .game.score import Score
from .player.player import Player
