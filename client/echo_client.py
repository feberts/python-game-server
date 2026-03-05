#!/usr/bin/env python3
"""
Echo client.

Not really a game, but occasionally useful for debugging and testing.

An unmodified copy of the message sent to the server is sent back to the client.
The game ends as soon as the message 'quit' is sent. Sending 'error' causes the
server to respond with an error message, which in turn results in an exception
being raised.
"""

from game_server_api import GameServerAPI, GameServerError, IllegalMove

game = GameServerAPI(server='127.0.0.1', port=4711, game='Echo', token='mygame', players=1)

my_id = game.join()
state = game.state()

while not state['gameover']:
    try:
        game.move(msg=input('Message: '))
    except IllegalMove as e:
        print(e)
        continue

    state = game.state()
    print('Echo:   ', state['echo'])
