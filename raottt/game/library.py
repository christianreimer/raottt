"""
Game Library
"""


#  import tinydb
import random

from ..game import opponent
from ..util import Color
from ..game.game import Game



class Library(object):
    """Stores all the live games and adds new games as needed."""

    def __init__(self, min_choices=3, verbose=False):
        """Initialize the factory"""
        self.min_choices = min_choices
        self.verbose = verbose
        self.available_games = {}
        self.in_play = {}
        # self.db = tinydb.TinyDB('library.json') 

    def load(self, data):
        """Load pre-created game data - used for testing"""
        for game_data in data:
            game = Game.load(game_data)
            self.available_games[game.ugid] = game

    def checkout(self, player):
        """Returns a game that is valid for this player to play."""
        if self.verbose:
            print("Library.checkout avail={} play={}".format(
                len(self.available_games), len(self.in_play)))

        color = player.color
        opp_color = opponent(color)

        possible_games = [g.ugid for g in self.available_games.values() if
                          g.next_color == color and
                          player.upid not in g.teams[opp_color]]

        # tf = lambda x, y: y not in x
        # query = tinydb.Query()

        # possible_games = self.db.search(query.teams.test(tf, player.upid) &
        #                                 (query.next_color == color))

        if self.verbose:
            print('Player %s had %s possible games' % (
                Color.me(player.color, player.upid),
                Color.yellow(len(possible_games))))

        for _ in range(self.min_choices - len(possible_games)):
            game = Game.new(player.color)
            possible_games.append(game.ugid)
            self.available_games[game.ugid] = game
            if self.verbose:
                print('Created game %s to fufill min_choices requirement' % (
                    Color.yellow(game.ugid)))
                print('There are now %s games in total' % (
                    len(self.available_games) + len(self.in_play)))

        ugid = random.choice(possible_games)
        game = self.available_games[ugid]
        self.in_play[ugid] = (game, player.upid)
        del self.available_games[ugid]
        return game

    def get_game(self, ugid, upid):
        """Returns the game associated with the specified ugid. Validates that
        the specified player had the game checked out."""
        print("Library.get_game avail={} play={}".format(
            len(self.available_games), len(self.in_play)))

        (game, checked_out_by) = self.in_play.get(ugid, (None, None))
        if upid != checked_out_by:
            return None
        return game

    def return_game(self, game):
        """Returns the specified game back into the pool after a turn."""
        assert game.ugid in self.in_play
        assert game.ugid not in self.available_games
        self.available_games[game.ugid] = game
        del self.in_play[game.ugid]
        print("Library.return_game avail={} play={}".format(
            len(self.available_games), len(self.in_play)))

    def remove_game(self, game):
        """Removes a game from play (because it has been won)."""
        assert game.ugid in self.in_play
        del self.in_play[game.ugid]
