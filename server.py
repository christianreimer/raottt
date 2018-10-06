"""
REST Api server built on flask.
"""

import json
import logging
import os
import random

import flask
from flask.ext.restful import Resource
from flask.ext.restful import Api
from flask_limiter import Limiter
import rauth

import raottt
from raottt import Game
from raottt import Player
from raottt import Score
from raottt.player.rest import RESTPlayer
from raottt.util import adapter

# pylint: disable=invalid-name

app = flask.Flask(__name__, static_url_path='')
app.config['RATELIMIT_STORAGE_URL'] = os.environ.get('REDISCLOUD_URL', None)
limiter = Limiter(app)
api = Api(app)
app.secret_key = '0xDecafBad'


def oh_no():
    """Create an Oh No! response"""
    msg = {'displayMsg': True,
           'message': ("<h2>On No!</h2>"
                       "<p>Looks like something went wrong, "
                       "please reload ...</p>"
                       "<p></p>"
                       "<i class='fa fa-bug fa-lg'>")}
    return json.dumps(msg)


class API_Game(Resource):
    """Game API endpoint"""

    # pylint: disable=no-self-use

    @limiter.limit('5 per second')
    def get(self, uid):
        """Return a game that can be played by the player with pid"""
        logging.debug('API_Game.get %s', uid)

        try:
            player = RESTPlayer(Player.load(uid).dumpd())
        except KeyError:
            logging.error('API_Game.get for unknown pid %s', uid)
            return flask.make_response(oh_no())

        # Apply any score change that results from other people moves
        score_change = Score.check_for_score_update(player.pid)
        if score_change:
            player.score += score_change
            player.save()

        game = Game.pick(player)
        return flask.make_response(json.dumps(adapter.enrich_message(game)))

    @limiter.limit('5 per second')
    def put(self, uid):
        """Apply a move to the specified game"""
        logging.debug('API_Game.put %s', flask.request.form)

        try:
            pid = flask.request.form['token']
            source = int(flask.request.form['source'])
            target = int(flask.request.form['target'])
        except (KeyError, ValueError):
            return flask.make_response(oh_no())

        player = RESTPlayer(Player.load(pid).dumpd())
        if not player:
            logging.error('API_Game.put from unknown pid %s', pid)
            return flask.make_response(oh_no())

        # Apply any score change that results from other people moves
        score_change = Score.check_for_score_update(player.pid)
        if score_change:
            player.score += score_change
            player.save()

        game = None

        try:
            game = Game.load(uid, validate=True, player=player)
        except ValueError:
            logging.error(
                'API_Game.put pid %s returned to abandoned gid %s',
                player.pid, uid)
        except KeyError:
            logging.error(
                'API_Game.put for unknown gid %s from pid %s', uid, pid)

        if not game:
            # Instead of giving the player an error, we just pretend to have
            # processed the move and they will get a new game. They probably
            # wont notice ...
            return flask.make_response(json.dumps({'displayMsg': False,
                                                   'message': '',
                                                   'score': player.score}))

        player.queue_move((source, target))
        score_change = game.make_move(player)
        player.score += score_change
        player.moves_made += 1
        player.save()

        game.inplay = False
        game.save()

        if game.game_over():
            game.cleanup(player.color)

            # There will be more points because the user participated in a
            # winning game
            score_additional = Score.check_for_score_update(player.pid)
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

    # pylint: disable=no-self-use

    @limiter.limit("10 per minute")
    def get(self, uid):
        """Load and return user specified by uid"""
        # If twitter name is set, then we came from the twitter login callback
        twitter_name = flask.session.pop('twitter_name', None)
        popup_type = twitter_name and 'newTwitter' or 'returningPlayer'

        logging.info('API_Player.get() uid:%s twitter_name:%s args:%s',
                     uid, twitter_name, flask.request.args)

        try:
            player = Player.load(uid, twitter_name)
        except KeyError as err:
            # Invalid (non-existing) user id, just create a new user
            logging.error(err)
            return self.post()

        if twitter_name and not player.twitter_creds:
            # User has just gotten their twitter creds
            player.name = twitter_name
            player.twitter_creds = True
            player.save()
            logging.info('Player %s got twitter_creds, now know as %s',
                         player.pid, twitter_name)

        # Apply any score change that results from other peoples moves
        score_change = Score.check_for_score_update(player.pid)
        if score_change:
            player.score += score_change
            player.save()

        return flask.make_response(json.dumps({'token': player.pid,
                                               'name': player.name,
                                               'color': player.color,
                                               'score': player.score,
                                               'creds': player.twitter_creds,
                                               'popupType': popup_type}))

    @limiter.limit('10 per minute')
    def post(self):
        """Create a new user"""
        player = RESTPlayer.new(random.choice(raottt.COLORS))
        player.save()
        return flask.make_response(json.dumps({'token': player.pid,
                                               'name': player.name,
                                               'color': player.color,
                                               'score': player.score,
                                               'popupType': 'newPlayer'}))


class API_Score(Resource):
    """Score API endpoint"""

    # pylint: disable=no-self-use
    # pylint: disable=too-few-public-methods

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

    # pylint: disable=no-self-use
    # pylint: disable=too-few-public-methods

    def get(self, uid):
        """Return debug information about this game"""
        logging.error('Debug gid %s', uid)
        try:
            game = Game.load(uid)
            game.show()
        except KeyError:
            logging.error(
                'API_Debug.get for unknown gid %s', uid)
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
    """API endpoint for login"""

    # pylint: disable=no-self-use
    # pylint: disable=too-few-public-methods

    def get(self, uid):
        """Start the login process for the given uid"""
        logging.info('API_Auth.get %s', uid)

        try:
            player = Player.load(uid, None)
        except KeyError as err:
            logging.error(err)
            return flask.make_response(oh_no())

        if player.twitter_creds:
            return flask.make_response(
                json.dumps({'popupType': 'logout',
                            'name': player.name}))

        # If the current user does not have twitter_creds, then bring up the
        # do you want to login popup
        logging.info('login_redirect_url: %s', flask.url_for('login_redirect'))
        return flask.make_response(
            json.dumps(
                {'popupType': 'startLogin',
                 'url': flask.url_for('login_redirect')}))


api.add_resource(API_Game, '/game/', '/game/<string:uid>/')
api.add_resource(API_Player, '/player/', '/player/<string:uid>/')
api.add_resource(API_Score, '/score/', '/score/<string:uid>/')
api.add_resource(API_Debug, '/debug/', '/debug/<string:uid>/')
api.add_resource(API_Auth, '/auth/', '/auth/<string:uid>/')


twitter = rauth.OAuth1Service(
    name='twitter',
    consumer_key='SyTUvaQ4zedclrQpRYSRjWa74',
    consumer_secret=os.environ.get('TWITTER_CONSUMER_SECRET', ''),
    request_token_url='https://api.twitter.com/oauth/request_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    access_token_url='https://api.twitter.com/oauth/access_token',
    base_url='https://api.twitter.com/1.1/'
)


@app.route('/login_redirect')
def login_redirect():
    """Redirect to the Twitter auth login service"""
    callback_url = flask.url_for('callback', _external=True)
    logging.info('***** callbacl_url: %s', callback_url)
    try:
        token = twitter.get_request_token(
            params={'oauth_callback': callback_url})
    except KeyError:
        logging.error('Failed to get token fro twitter callback')
        logging.error('Received: %s', str(token))
        return flask.redirect(flask.url_for('root'))

        logging.info('login_redirect callback url %s token %s', callback_url, token)
    return flask.redirect(twitter.get_authorize_url(token[0]))


@app.route('/callback')
def callback():
    """Callback from the Twitter auth login service"""
    logging.info('callback args %s', flask.request.args)

    if 'denied' in flask.request.args:
        logging.info('Player denied Twitter auth request')
        return flask.redirect(flask.url_for('root'))

    token1 = flask.request.args['oauth_token']
    token2 = flask.request.args['oauth_verifier']

    oauth_session = twitter.get_auth_session(
        token1,
        token2,
        data={'oauth_verifier': flask.request.args['oauth_verifier']}
    )

    player_info = oauth_session.get('account/verify_credentials.json').json()
    name = player_info.get('screen_name')
    flask.session['twitter_name'] = name
    return flask.redirect(flask.url_for('root'))


@app.route('/')
def root():
    """Route to serve the static index.html page"""
    return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0')  # , debug=True, port=8888)

