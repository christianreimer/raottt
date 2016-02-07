"""
REST Api server built on flask.
"""

# pylint: disable=R0201
# pylint: disable=C0103
# pylint: disable=W0232
# pylint: disable=F0401

import json
import logging
import os
import random

import flask
from flask.ext.restful import Resource
from flask.ext.restful import Api
from flask_limiter import Limiter

from raottt import Game
from raottt import Player
from raottt import Score
from raottt.player.rest import RESTPlayer
from raottt.util import adapter


app = flask.Flask(__name__, static_url_path='')
app.config['RATELIMIT_STORAGE_URL'] = os.environ['REDISCLOUD_URL']
limiter = Limiter(app)
api = Api(app)
app.secret_key = '0xDecafBad'


def oh_no():
    """Create an Oh No! response"""
    msg = {'displayMsg': True,
           'message': ("<p>On No!</p>"
                       "<p>Looks like something went wrong, please reload ...")}
    return json.dumps(msg)


class API_Game(Resource):
    """Game API endpoint"""

    @limiter.limit('5 per second')
    def get(self, uid):
        """Return a game that can be played by the player with pid"""
        logging.debug('API_Game.get {}'.format(uid))
  
        try:
            player = RESTPlayer(Player.load(uid).dumpd())
        except KeyError:
            logging.error('API_Game.get for unknown pid {}'.format(uid))
            return flask.make_response(oh_no())
        
        # Apply any score change that results from other people moves
        score_change = Score.check_for_score_upate(player.pid)
        if score_change:
            player.score += score_change
            player.save()

        game = Game.pick(player)
        return flask.make_response(json.dumps(adapter.enrich_message(game)))

    @limiter.limit('5 per second')
    def put(self, uid):
        """Apply a move to the specified game"""
        logging.debug('API_Game.put {}'.format(flask.request.form))

        try:
            pid = flask.request.form['token']
            source = int(flask.request.form['source'])
            target = int(flask.request.form['target'])
        except (KeyError, ValueError):
            return flask.make_response(oh_no())

        player = RESTPlayer(Player.load(pid).dumpd())
        if not player:
            logging.error('API_Game.put from unknown pid {}'.format(pid))
            return flask.make_response(oh_no())

        # Apply any score change that results from other people moves
        score_change = Score.check_for_score_upate(player.pid)
        if score_change:
            player.score += score_change
            player.save()

        game = None

        try:
            game = Game.load(uid, validate=True, player=player)
        except ValueError:
            logging.error(
                'API_Game.put pid {} returned to abandoned gid {}'.format(
                    player.pid, uid))
        except KeyError:
            logging.error(
                'API_Game.put for unknown gid {} from pid {}'.format(gid, pid))

        if not game:
            # Instead of giving the player an error, we just pretend to have
            # processed the move and they will get a new game. They probably
            # wont event notice ...
            return flask.make_response(json.dumps({'displayMsg': False,
                                                   'message': '',
                                                   'score': player.score}))

        player.queue_move((source, target))
        score_change = game.make_move(player)
        player.score += score_changey
        player.moves_made += 1
        player.save()

        game.inplay = False
        game.save()
                
        if game.game_over():
            game.cleanup(player.color)

            # There will be more points because the user participated in a
            # winning game
            score_additional = Score.check_for_score_upate(player.pid)
            player.score += score_additional
            player.save()

            return flask.make_response(json.dumps(
                {'displayMsg': True,
                 'message': ('<p>Nice Move!</P><p>You just added {} points to '
                             'your own score, and you helped out all the other '
                             '{} players who participated in this game.</p>'
                             ''.format(score_change + score_additional, 
                                       player.color)),
                 'score': player.score}))

        return flask.make_response(json.dumps({'displayMsg': False,
                                               'message': '',
                                               'score': player.score}))


class API_Player(Resource):
    """Player API endpoint"""

    @limiter.limit("10 per minute")
    def get(self, uid):
        """Return the user specified by uid"""
        try:
            player = Player.load(uid)
        except KeyError as err:
            # Invalid (non-existing) user id, just create a new user
            logging.error(err)
            return self.post()

        # Apply any score change that results from other people moves
        score_change = Score.check_for_score_upate(player.pid)
        if score_change:
            player.score += score_change
            player.save()

        flask.session['count'] = 0

        return flask.make_response(json.dumps({'token': player.pid,
                                               'name': player.name,
                                               'color': player.color,
                                               'score': player.score,
                                               'returning': 1}))

    @limiter.limit('10 per minute')
    def post(self):
        """Create a new user"""
        player = RESTPlayer.new(random.choice(('Red', 'Blue')))
        player.save()
        return flask.make_response(json.dumps({'token': player.pid,
                                               'name': player.name,
                                               'color': player.color,
                                               'score': player.score,
                                               'returning': 0}))


class API_Score(Resource):
    """Score API endpoint"""

    @limiter.limit('1 per second')
    def get(self, uid):
        """Return score information for this user"""
        player = Player.load(uid)
        total_lst = Score.get_global_score()
        total_map = {total_lst[0]['color']: total_lst[0],
                     total_lst[1]['color']: total_lst[1]}

        return flask.make_response(
            json.dumps({'score': player.score,
                        'turns': player.moves_made,
                        'games': player.games_participated_in,
                        'totalTurns': total_map['Red']['turns'] + 
                                      total_map['Blue']['turns'],
                        'redWins': total_map['Red']['wins'],
                        'blueWins': total_map['Blue']['wins']}))


class API_Debug(Resource):
    """Debug API endpoint"""

    def get(self, uid):
        """Return debug information about this game"""
        logging.error('Debug gid {}'.format(uid))
        try:
            game = Game.load(uid)
            game.show()
        except KeyError:
            logging.error(
                'API_Debug.get for unknown gid {}'.format(gid))
            return flask.make_response(oh_no())

        return flask.make_response(
            json.dumps(
                {'gid': game.gid,
                 'value': game.score.value,
                 'nextColor': game.next_color,
                 'checkout': str(game.checkout),
                 'player': game.player,
                 'score': game.score.dumpd()}))


class API_Auth(Resource):
    """Auth API Endpoint"""

    self.twitter = OAuth1Service(
        name='twitter',
        consumer_key='Gj4uIVgztBtLcdZXquupij9ph',
        consumer_secret='J4kraCJ2C8aXjtHQOPjviAzTZ9pCkx4m4JTvftjmRhoMHEke7h',
        request_token_url='https://api.twitter.com/oauth/request_token',
        authorize_url='https://api.twitter.com/oauth/authorize',
        access_token_url='https://api.twitter.com/oauth/access_token',
        base_url='https://api.twitter.com/1.1/'
    )
    
    def get(self, uid):
        token = flask.session.get('token', None)
        if not token:
            self.twitter_login()
        else:
            self.twitter_callback(flask.request.args)

    def twitter_login(self):
        token = self.twitter.get_request_token(
            params={'oauth_callback': url_for('get', _external=True)})
        flask.session['token'] = token
        url = twitter.get_authorize_url(token[0])
        print('Callback URL: '.format(url_for('get', _external=True)))
        return flask.redirect(url)

    def twitter_callback(self):
        token = flask.session['token']
        oauth_session = twitter.get_auth_session(
            token[0],
            token[1],
            data={'oauth_verifier': request.args['oauth_verifier']}
        )
    
        me = oauth_session.get('account/verify_credentials.json').json()
        username = me.get('screen_name')
        print('username:{}'.format(username))
        return flask.make_response("Hello {}".format(username))



api.add_resource(API_Game, '/game/', '/game/<string:uid>/')
api.add_resource(API_Player, '/player/', '/player/<string:uid>/')
api.add_resource(API_Score, '/score/', '/score/<string:uid>/')
api.add_resource(API_Debug, '/debug/', '/debug/<string:uid>/')
api.add_resource(API_Auth, '/auth/', '/auth/<string:uid>/')


@app.route('/')
def root():
    """Route to serve the static index.html page"""
    return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=8888)

