#!/usr/bin/env python

"""
Simple harness that will run the TTT game. Can do any of Human vs Human,
Human vs Computer, or Computer vs Computer.

Usage: play.py [--blue=<b>] [--red=<r>] [--games=<n>] [--show]

Options:
    --blue=<b>      Blue player type (Human or Computer) [default: Computer]
    --red=<r>       Red plater type (Human or Computer) [default: Computer]
    --games=<n>     Number of games to play [default: 1]
    --show          Show boards between games [default: false]
"""

from docopt import docopt
from raottt.game import opponent
from raottt.game.game import Game
from raottt.player.computer import ComputerPlayer
from raottt.player.human import HumanPlayer
from raottt.util import Color


def toggle(item1, item2):
    """Return a generator that will contnually toggle between the two items"""
    while True:
        yield item1
        yield item2


def run_game(player1, player2, max_rounds, show=True):
    """Run a game between player1 and player2 for max_rounds and then return
    the game state"""
    game = Game.new('Blue')
    player_toggle = toggle(player1, player2)
    if show:
        game.show()
        print()

    for _ in range(max_rounds):
        if game.game_over():
            break

        player = player_toggle.next()
        game.make_move(player)
        game.validate()

        print(Color.me(player.color, "{}'s Score: {}".format(
            player.name, player.score)))

        if show:
            game.show()
            print()

    return game


def main():
    """main"""
    args = docopt(__doc__)

    for arg in ('--blue', '--red'):
        if not args[arg] in ('Human', 'Computer'):
            print('Invalid argument for {}, '
                  'valid options are Human or Computer'.format(args[arg]))
            return

    blue = HumanPlayer('Blue', opponent) if args['--blue'] == 'Human' else \
           ComputerPlayer('Blue', opponent)

    red = HumanPlayer('Red', opponent) if args['--red'] == 'Human' else \
          ComputerPlayer('Red', opponent)


    for _ in range(int(args["--games"])):
        game = run_game(blue, red, 999999, args['--show'])
        print(Color.me(game.game_over(), '{} wins in {} moves!!!'.format(
            game.game_over(), game.score_tracker['num_moves'])))


if __name__ == '__main__':
    main()
