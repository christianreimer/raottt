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
    to_client['netxPlayer'] = dump['nextPlayer']
    to_client['ugid'] = dump['ugid']

    avail_sources = [s for (s, _) in game.board.available_moves(game.next_color)]
    square_lst = dump['board']
    for i, square in enumerate(square_lst):
        square['movable'] = i in avail_sources
    to_client['board'] = square_lst

    return to_client
