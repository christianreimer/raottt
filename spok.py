"""
Spok is a simple AI player in the raottt game.

Usage: spok.py play --red=<r> --blue=<b> [--frequency=<s>]
       spok.py clean [--ttl=<t>]
       spok.oy create

Options:
    --red=<r>           The pid for the red player
    --blue=<b>          The pid for the blue player
    --frequency=<s>     How many seconds to sleep between moves [default: 10]
    --ttl=<t>           Seconds before a game is abandoned [default: 3600]
"""

import datetime
import logging
import random
import time

from docopt import docopt

import raottt
from raottt import Game
from raottt.player.computer import ComputerPlayer

from raottt.util import database
MongoDb = database.DatabaseConnection()


def cleanup(ttl):
    """Remove the inplay flag for abandoned games"""
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(seconds=ttl)
    game_lst = [g for g in MongoDb.game.find({'checkout': {'$lt': cutoff}})]
    for game in game_lst:
        game = Game.load(game['gid'])
        logging.debug('Spok force returning game {} checked out at {}'.format(
            game.gid, game.checkout))
        game.inplay = False
        game.player = None
        game.checkout = None
        game.save()


def player_and_turns(player_red, player_blue):
    """Return the number of turns to make and which color to play for."""
    avail_red = MongoDb.game.find({'next_color': 'Red', 'inplay': False}).count()
    avail_blue = MongoDb.game.find({'next_color': 'Blue', 'inplay': False}).count()

    if avail_red > avail_blue:
        return player_red, avail_blue // 2 + (avail_red - avail_blue) // 2
    elif avail_blue > avail_red:
        return player_blue, avail_red // 2 + (avail_blue - avail_red) // 2
    else:
        player = random.choice((player_red, player_blue))
        return player, avail_red // 2


def take_turn(player):
    """Take a turn"""
    try:
        game = raottt.Game.pick(player, create_if_needed=False)
    except IndexError:
        return

    game.make_move(player)
    game.inplay = False
    game.save()

    if game.game_over():
        game.cleanup(player.color)


def create():
    """Create new player"""
    red = ComputerPlayer.new('Red')
    red.save()
    print('Created {}'.format(red))

    blue = ComputerPlayer.new('Blue')
    blue.save()
    print('Created {}'.format(blue))


def loop(pid_red, pid_blue, frequency):
    """Loop forever and take turns"""
    red = ComputerPlayer(raottt.Player.load(pid_red).dumpd())
    blue = ComputerPlayer(raottt.Player.load(pid_blue).dumpd())

    while True:
        time.sleep(frequency)
        player, turns = player_and_turns(red, blue)
        logging.info('{} Spok should take {} turns'.format(player.color, turns))
        for _ in range(turns):
            take_turn(player)


def main():
    """main"""
    args = docopt(__doc__)
    
    if args['create']:
        create()
        return

    if args['play']:
        loop(args['--red'], args['--blue'], int(args['--frequency']))

    if args['clean']:
        cleanup(int(args['--ttl']))



if __name__ == '__main__':
    main()
