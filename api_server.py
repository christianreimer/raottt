"""
REST Api server built on flask.
"""

# pylint: disable=R0201
# pylint: disable=C0103
# pylint: disable=W0232
# pylint: disable=F0401

import json
import logging

import flask
from flask.ext.restful import Resource
from flask.ext.restful import Api

from raottt import Game
from raottt import Player
from raottt import Score
from raottt.player.rest import RESTPlayer
from raottt.player.computer import ComputerPlayer
from raottt.util import adapter


spok = ComputerPlayer.new('Blue')
spok.save()

app = flask.Flask(__name__, static_url_path='')
api = Api(app)


def oh_no():
    """Create an Oh No! response"""
    msg = {'displayMsg': True,
           'message': ("<p>On No!</p>"
                       "<p>Looks like something went wrong, please reload ...")}
    return json.dumps(msg)


class API_Game(Resource):
    """Game API endpoint"""

    def get(self, uid):
        """Return a game that can be played by the player with pid"""
        logging.debug('API_Game.get {}'.format(uid))
  
        player = RESTPlayer(Player.load(uid).dumpd())
        if not player:
            logging.error('API_Game get for unknown pid {}'.format(uid))
            return flask.make_response(oh_no())
        
        # Apply any score change that results from other people moves
        score_change = Score.check_for_score_upate(player.pid)
        if score_change:
            player.score += score_change
            player.save()

        game = Game.pick(player)
        if not game:
            logging.error('Unable to pick a game for player {}'.format(uid))
            return flask.make_response(oh_no())

        return flask.make_response(json.dumps(adapter.enrich_message(game)))

    def put(self, uid):
        """Apply a move to the specified game"""
        logging.debug('API_Game.put: {}'.format(flask.request.form))

        try:
            pid = flask.request.form['token']
            source = int(flask.request.form['source'])
            target = int(flask.request.form['target'])
        except (KeyError, ValueError):
            return flask.make_response(oh_no())

        player = RESTPlayer(Player.load(pid).dumpd())
        if not player:
            logging.error('API_Game put from unknown pid {}'.format(pid))
            return flask.make_response(oh_no())

        player.score += Score.check_for_score_upate(player.pid)

        player.queue_move((source, target))
        game = Game.load(uid)
        if not game:
            logging.error('API_Game put for unknown gid {} from pid {}'.format(
                gid, pid))
            return flask.make_response(oh_no())

        game.make_move(player)
        game.save()
        player.save()
        
        if game.game_over():
            _ = game.cleanup()
            return flask.make_response(json.dumps({'displayMsg': True,
                                        'message': 'You Won!',
                                        'score': player.score}))
        game.make_move(spok)
        game.inplay = False
        game.save()

        if game.game_over():
            _ = game.cleanup()
            return flask.make_response(json.dumps({'displayMsg': True,
                                        'message': 'You Loose :(',
                                        'score': player.score}))

        return flask.make_response(json.dumps({'displayMsg': False,
                                    'message': 'Move Processed',
                                    'score': player.score}))


class API_Player(Resource):
    """Player API endpoint"""

    def get(self, uid):
        """Return the user specified by uid"""
        player = Player.load(uid)

        # Apply any score change that results from other people moves
        score_change = Score.check_for_score_upate(player.pid)
        if score_change:
            player.score += score_change
            player.save()

        return flask.make_response(json.dumps({'token': player.pid,
                                    'name': player.name,
                                    'color': player.color,
                                    'score': player.score}))

    def post(self):
        """Create a new user"""
        player = RESTPlayer.new('Red')
        player.save()
        return flask.make_response(json.dumps({'token': player.pid,
                                    'name': player.name,
                                    'color': player.color,
                                    'score': player.score}))


api.add_resource(API_Game, '/game/', '/game/<string:uid>/')
api.add_resource(API_Player, '/player/', '/player/<string:uid>/')


@app.route('/')
def root():
    """Route to serve the static index.html page"""
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8888) # , port=8888, debug=True)
    # app.run(debug=True)  # port=8888, debug=True)

