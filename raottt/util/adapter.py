"""
Adapts the JSON messages between the UI and the backend. Basically adds
additional elements to the outgoing JSON object which makes it easier to
layout things on the client side.
"""


def enrich_message(game):
    """Enriches the game json dump for the UI"""
    dump = game.dump()

    to_client = {}
    to_client['offBoard'] = dump['offBoard']
    to_client['nextPlayer'] = dump['nextPlayer']
    to_client['ugid'] = dump['ugid']

    avail_sources = [s for (s, _) in game.board.available_moves(game.next_color)]
    square_lst = dump['board']
    print(square_lst)
    for i, square in enumerate(square_lst):
        square['movable'] = i in avail_sources
    to_client['board'] = square_lst

    if to_client['offBoard']:
        to_client['instructions'] = 'Click on an empty square to add a %s piece' % (
            to_client['nextPlayer'], )

    elif all([s['movable'] for s in square_lst]):
        to_client['instructions'] = 'Drag a %s piece to an empty square' % (
            to_client['nextPlayer'], )
    else:
        to_client['instructions'] = ('Drag a %s piece to an empty square (it must be the '
            'piece with count 1...)' % (
            to_client['nextPlayer'], ))

    return to_client
