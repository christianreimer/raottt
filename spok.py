"""
Spok is a simple AI player in the raottt game.

Usage: spok play (--env | (--red=<r> --blue=<b>)) [--ttl=<t>] [--stock=<m>]
                [--frequency=<s>] [--lower=<l>] [--upper=<u>] [--games=<n>]
       spok init

Options:
    --red=<r>         Pid of the red player
    --blue=<b>        Pic of the blue player
    --ttl=<t>         Seconds before a game is abandoned [default: 3600]
    --stock=<m>       Minimum number of available games [default: 25]
    --frequency=<s>   How many sec to sleep between plays [default: 10]
    --lower=<l>       Lower bound of rounds to play per game [default: 6]
    --upper=<u>       Upper bound of rounds to play per game [default: 12]
    --games=<n>       Number of games to create when stock is low [default: 10]
"""

import datetime
import logging
import random
import os
import time

from docopt import docopt

import raottt
from raottt import Game
from raottt.player.computer import ComputerPlayer

from raottt.util import database
MongoDb = database.DatabaseConnection()


def toggle(item1, item2):
    """Return a generator that will contnually toggle between the two items"""
    while True:
        yield item1
        yield item2


def create_games(num_games, lower, upper):
    """Create ``num_games`` games"""
    blue = ComputerPlayer.new('Blue')
    red = ComputerPlayer.new('Red')

    for i in range(num_games):
        if random.choice(('Red', 'Blue')) == 'Red':
            game = Game.new('Red')
            player_toggle = toggle(red, blue)
        else:
            game = Game.new('Blue')
            player_toggle = toggle(blue, red)

        for turns in range(random.randint(lower, upper)):
            if game.game_over():
                break

            player = player_toggle.__next__()
            game.make_move(player)
            game.validate()

        logging.info('Spok created game with {} turns, next player {}'.format(
            turns+1, game.next_color))
        game.save()


def cleanup(ttl):
    """Remove the inplay flag for abandoned games"""
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(seconds=ttl)
    game_lst = [g for g in MongoDb.game.find({'checkout': {'$lt': cutoff}})]
    for game in game_lst:
        game = Game.load(game['gid'])
        logging.info('Spok force returning game {} checked out at {}'.format(
            game.gid, game.checkout))
        game.inplay = False
        game.player = None
        game.checkout = None
        game.save()


def player_and_turns(player_red, player_blue):
    """Return the number of turns to make and which color to play for."""
    avail_red = MongoDb.game.find({'next_color': 'Red', 'inplay': False}).count()
    avail_blue = MongoDb.game.find({'next_color': 'Blue', 'inplay': False}).count()

    logging.info('Spok game availability red={} blue={}'.format(
        avail_red, avail_blue))

    if avail_red > avail_blue:
        return player_red, max(1, (avail_red - avail_blue) // 2)
    elif avail_blue > avail_red:
        return player_blue, max(1, (avail_blue - avail_red) // 2)
    else:
        player = random.choice((player_red, player_blue))
        return player, avail_red // 3


def take_turns(turns, player):
    """Take ``turns`` turns"""
    for _ in range(turns):
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


def init():
    """Init database and users"""
    database.nuke(True)
    database.init()

    red = ComputerPlayer.new('Red')
    red.save()
    blue = ComputerPlayer.new('Blue')
    blue.save()

    return red, blue


def main():
    """main"""
    args = docopt(__doc__)
    
    if args['init']:
        msg = 'Are you sure you want to init (all data will be erased): '
        answer = input(msg)
        if answer.upper() in ('YES', 'Y'):
            red, blue = init()
            print('Created red={} blue={}'.format(red.pid, blue.pid))
            return

    if args['--env']:
        pid_red = os.environ['SPOK_RED']
        pid_blue = os.environ['SPOK_BLUE']
    else:
        pid_red = args['--red']
        pid_blue = args['--blue']

    sleep_sec = int(args['--frequency'])
    ttl = int(args['--ttl'])
    min_stock = int(args['--stock'])
    lower = int(args['--lower'])
    upper = int(args['--upper'])
    num_games = int(args['--games'])

    red = ComputerPlayer(raottt.Player.load(pid_red).dumpd())
    blue = ComputerPlayer(raottt.Player.load(pid_blue).dumpd())

    while True:
        time_start = datetime.datetime.now()

        # Perform moves to keep the game running
        player, turns = player_and_turns(red, blue)
        logging.info('Spok should take {} turns for the {} team'.format(
            turns, player.color))
        take_turns(turns, player)

        # Cleanup abandoned games
        cleanup(ttl)

        # Make sure there are games available to play
        stock = MongoDb.game.find({'inplay': False}).count()
        logging.info('Spok current stock is at {} (min={})'.format(
            stock, min_stock))

        if min_stock > stock:
            create_games(num_games, lower, upper)

        time_elapsed = datetime.datetime.now() - time_start
        if time_elapsed.seconds > sleep_sec:
            logging.error('Spok took {} sec to complete an itration'.format(
                time_elapsed.seconds))

        time_to_sleep = max(1, sleep_sec - time_elapsed.seconds)
        logging.debug('Spok sleeping for {} seconds'.format(time_to_sleep))
        time.sleep(time_to_sleep)


if __name__ == '__main__':
    main()

