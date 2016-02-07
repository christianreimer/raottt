"""
Functionality that adapts the server's python representation to the needs of
the JavaScript UI client.
"""


def enrich_message(game):
    """Enriches the game json dump for the UI"""
    dump = game.dumpjs()

    to_client = {}
    to_client['offBoard'] = dump['offBoard']
    to_client['nextPlayer'] = dump['nextPlayer']
    to_client['ugid'] = dump['ugid']

    avail_sources = [s for (s, _) in game.board.available_moves(game.next_color)]
    square_lst = dump['board']

    for i, square in enumerate(square_lst):
        square['movable'] = i in avail_sources
    to_client['board'] = square_lst

    if to_client['offBoard']:
        to_client['instructions'] = (
            'Click on an empty square to add a new {} piece'.format(
                to_client['nextPlayer']))

    elif len([s for s in square_lst if s['movable']]) == 1:
        to_client['instructions'] = (
            'Drag the {} piece with count 1 to an empty square. It is the '
            'only one you can move ...'.format(to_client['nextPlayer']))
    else:
        to_client['instructions'] = (
            'Drag any {} piece to any empty square.'.format(
                to_client['nextPlayer']))

    to_client['gameId'] = game.gid
    to_client['gameValue'] = game.score.value

    return to_client
