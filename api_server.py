"""
REST Api server built on flask.
"""

# pylint: disable=R0201
# pylint: disable=C0103
# pylint: disable=W0232
# pylint: disable=F0401

import json

from flask import Flask
from flask import request
from flask import make_response
from flask.ext.restful import Resource
from flask.ext.restful import Api

from raottt.game import opponent
from raottt.game.library import Library
from raottt.player.player import Bench
from raottt.player.rest import RESTPlayer
from raottt.player.computer import ComputerPlayer
from raottt.util import adapter


library = Library()
# library.load(json.loads(open('games.json').read()))
bench = Bench()
spok = ComputerPlayer('Red', opponent, name='Spok')
bench.register(spok)
app = Flask(__name__, static_url_path='')
api = Api(app)


def oh_no():
    """Create an Oh No! response"""
    msg = {'displayMsg': True,
           'message': ("On No!<br><br>Looks like something went wrong, please "
                       "try to reload ...")}
    return json.dumps(msg)


def res_wrap(data):
    """Return a respons"""
    print('\n%s\n' % (50 * '='))
    return make_response(data)


class Game(Resource):
    """Interacts with the game library

    GET /game/id will return a new game that can be played by the user with id
    PUT /game/id will apply a move to the given game
    """
    def get(self, uid):
        """doc string"""
        player = bench[uid]
        if not player:
            print('ERROR: got request for unknown player: {}'.format(uid))
            return res_wrap(oh_no())

        game = library.checkout(player)
        if not game:
            print('ERROR: could not find game for player: {}'.format(uid))
            return res_wrap(oh_no())

        return res_wrap(json.dumps(adapter.enrich_message(game)))

    def put(self, uid):
        """doc string"""
        # print(request.form)
        try:
            token = request.form['token']
            source = int(request.form['source'])
            target = int(request.form['target'])
        except (KeyError, ValueError):
            return res_wrap(oh_no())

        player = bench[token]
        if not player:
            print('ERROR: player {} not found!'.format(token))
            return res_wrap(oh_no())

        player.queue_move((source, target))
        game = library.get_game(uid, token)
        if not game:
            print('ERROR: game uid {} player {} not found'.format(uid, player))
            return res_wrap(oh_no())

        game.make_move(player)
        print("After my move")
        game.show()

        if game.game_over():
            game.cleanup(bench)
            library.remove_game(game)
            return res_wrap(json.dumps({'displayMsg': True,
                                        'message': 'You Won!',
                                        'score': player.score}))

        game.make_move(spok)
        print("After Spock's move")
        game.show()
        if game.game_over():
            game.cleanup(bench)
            library.remove_game(game)
            return res_wrap(json.dumps({'displayMsg': True,
                                        'message': 'You Loose :(',
                                        'score': player.score}))

        library.return_game(game)
        return res_wrap(json.dumps({'displayMsg': False,
                                    'message': 'Move Processed',
                                    'score': player.score}))


class Player(Resource):
    """Track stats for users

    GET  /player/puid will return the stats for the given player
    POST /player/ will create a new player
    """
    def get(self, uid):
        """Return the user's stats"""
        player = bench[uid]
        return res_wrap(json.dumps({'name': player.name,
                                    'color': player.color}))

    def post(self):
        """Create a new user"""
        player = RESTPlayer('Blue', opponent)
        bench.register(player)
        print("***** NEW USER CREATED *****")
        print("* I shall call you {}".format(player.name))
        print("* I will use id {}".format(player.upid))
        return res_wrap(json.dumps({'token': player.upid,
                                    'name': player.name,
                                    'color': player.color}))


api.add_resource(Game, '/game/', '/game/<string:uid>/')
api.add_resource(Player, '/player/', '/player/<string:uid>/')


@app.route('/')
def root():
    """Route to serve the static index.html page"""
    return app.send_static_file('index.html')

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=8888, debug=True)
    app.run(port=8888, debug=True)

