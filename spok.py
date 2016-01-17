"""
Spok is a simple AI player in the raottt game.

Usage: spok.py create
       spok.py play --red=<r> --blue=<b> [--lookahead=<l>] [--frequency=<s>]
       spok.py clean [--ttl=<t>]

Options:
    --red=<r>           The pid for the red player
    --blue=<b>          The pid for the blue player
    --lookahead=<l>     The number of moves to lookahead [default: 3]
    --frequency=<s>     How many seconds to sleep between moves [default: 3]
    --ttl=<t>           Seconds before a game is abandoned [default: 3600]
"""

import time

from docopt import docopt

import raottt
from raottt.player.computer import ComputerPlayer

from raottt.util import database
MongoDb = database.DatabaseConnection()


def turns_and_color(player_red, player_blue):
    """Return the number of turns to make and which color to play for."""
    # Return min(color) / 2 + max(color) - min(color)
    avail_red = MongoDb.find({'next_color': 'Red'}).count()
    avail_blue = MongoDb.find({'next_color': 'Blue'}).count()

    if avail_red > avail_blue:
        return player_red, avail_blue / 2 + (avail_red - avail_blue)
    elif avail_blue > avail_red:
        return player_blue, avail_red / 2 + (avail_blue - avail_red)



def take_turn(player):
    """Take a turn"""
    try:
        game = raottt.Game.pick(player, create_if_needed=False)
    except IndexError:
        # Nothing to do
        print('No games waiting for a move, snoozing ....')
        return

    game.make_move(player)
    game.inplay = False
    game.save()

    if game.game_over():
        game.cleanup(player.color)


def create(color):
    """Create new player"""
    player = ComputerPlayer.new(color)
    player.save()
    print('Created {}'.format(player))


def main():
    """main"""
    args = docopt(__doc__)
    
    if args['create']:
        create(args['--red'] and 'Red' or 'Blue')
        return

    player = ComputerPlayer(raottt.Player.load(args['--pid']).dumpd())

    while True:    
        time.sleep(int(args['--frequency']))
        take_turn(player)


if __name__ == '__main__':
    main()
