"""
Implments the rules to calculate how much to update the user's score by after
a move.

+1 for every move
+1 if move improved the value of the board for your color
+2 if you change from being behind to ahead
+2 if a chain you helped with wins  (??)
+5 if you make the winning move

-4 if the game is lost on the next move
-1 if a chain you helped with looses
-1 if you lower the value of the board
-1 if you change from being ahead to behind


The Game object should keep a tuple of the previous person to make a move
(Player, Score, Ratio) then we can compare in the post_move_score_update if the
current move (that has just completed) improved or worsened things.

Also, if the game ends at this point then we can modify the score of the
previous person who made it happen ...

Questions:
Shoulds we keep track of ALL the people who have participated in the
game (and the number of turns they took - and possibly the ration of imprcements
and decreases??)? That way, when a game ends, we can allocation a number of
point to the winning team (the older the game the more points) and hand them out
to the people who partiipated ...

How should I be notifying you about a score change that happened becuse of a
subsequent move?? Go all out and do smily and frowney faces? "BigGorillaMonkey
just won a game where you made the previous move .. Oh shame on you ..." or
"Great News! BigGorillaMonkey just made the winning move for team Red in a
game that you helped. He was standing on the shoulders of giants. Yours
Shoulders (among others). Great stuff. Have +X points"

"""


import math

from ..game import opponent


def empty_score_tracker(ugid):
    """blah"""
    return {'teams': {'Red': {}, 'Blue': {}},
            'previous': {'Red': [(0, 0, 0)], 'Blue': [(0, 0, 0)]},
            'num_moves': 0,
            'ugid': ugid}


# pylint: disable=too-many-arguments

def post_move_score_update(tracker, new_score, new_ratio, winner, color, upid):
    """blah"""
    _, prev_score, _ = tracker['previous'][color][-1]
    _, _, prev_ratio = tracker['previous'][opponent(color)][-1]

    # Record the fact that this upid participated in the game
    tracker['teams'][color][upid] = tracker['teams'][color].get(upid, 0) + 1
    tracker['previous'][color].append((upid, new_score, new_ratio))
    tracker['num_moves'] += 1

    # Calculate the score this player will get based on the rules:
    # +1 for every move
    # +1 if move improved the value of the board for your color
    # -1 if you lower the value of the board for your color
    # +2 if you change your color from being behind to ahead
    # -1 if you change your color from being ahead to behind
    # +3 if you make the winning move
    score = 1
    if new_score > prev_score:
        score += 1
    elif new_score < prev_score:
        score -= 1

    if prev_ratio < 0.50 and new_ratio > 0.50:
        score += 2
    elif prev_ratio > 0.50 and new_ratio < 0.50:
        score -= 1

    if winner == color:
        score += 3

    return score, tracker


def show_score(tracker):
    """Prints the score to the console"""
    print('Game: {}'.format(tracker['ugid']))
    print('Num Moves: {}'.format(tracker['num_moves']))
    print('Team Red:  {}'.format(tracker['teams']['Red']))
    print('Team Blue: {}'.format(tracker['teams']['Blue']))


def post_game_score_update(winning_color, tracker, bench):
    """Updates scores as a result of a game being won. THe idea is that all the
    player (upids) that participated in the game share in the glory (or shame).
    The total value of the game is dependent on the number of moves that were
    taken, and each player gets a part of the point proportionate to the number
    of moves that player made."""
    points = tracker['num_moves']
    win_factor = 2
    team_size = len(tracker['teams'][winning_color])
    for upid, moves in tracker['teams'][winning_color].items():
        player = bench[upid]
        if not player:
            print("ERROR: could not find for upid {}".format(upid))
            continue
        add_score(player, moves, win_factor, points, team_size)

    loss_factor = -1
    team_size = len(tracker['teams'][opponent(winning_color)])
    for upid, moves in tracker['teams'][opponent(winning_color)].items():
        player = bench[upid]
        if not player:
            print("ERROR: could not find for upid {}".format(upid))
            continue
        add_score(player, moves, loss_factor, points, team_size)


def add_score(player, moves, factor, points, team_size):
    """Adds to the player's score."""
    player.score += factor * math.ceil(points/team_size) * moves
