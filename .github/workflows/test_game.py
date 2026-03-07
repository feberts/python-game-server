#!/usr/bin/env python3
"""
Playing through a game, provoking all error cases.
"""

from game_server_api import GameServerAPI, GameServerError, IllegalMove

import threading
import traceback

SERVER = '127.0.0.1'
PORT = 4711

end = threading.Event()
sync = threading.Event()

error = False

def fail(msg):
    global error
    error = True
    print(f'ERROR: {msg}')
    end.set()

def synchronize_threads():
    sync.set()
    sync.clear()
    sync.wait()

moves = [(1, True), (2, True), (4, True), (4, False), (42, False), (5, True), (7, True)]

def play():
    try:
        game = GameServerAPI(SERVER, PORT, 'TicTacToe', 'test', 2)
        my_id = game.join()
        state = game.state()

        if my_id not in state['current']:
            try:
                game.move(position=1)
                fail('no exception although not players turn')
            except GameServerError:
                pass

        synchronize_threads()

        while len(moves):
            if state['gameover']: fail('gameover although game has not ended')
            if state['winner'] is not None: fail('winner although game still active')

            if my_id in state['current']:
                try:
                    move, legal = moves.pop(0)
                    game.move(position=move)
                    if not legal: fail('no exception despite illegal move')
                except IllegalMove:
                    if legal: fail('exception despite legal move')

            synchronize_threads()
            state = game.state()

        if not state['gameover']: fail('no gameover after final move')

        try:
            game.move(position=1)
            fail('no exception when performing move after game has ended')
        except GameServerError:
            pass

        if state['winner'] is None: fail('no winner despite win')
        if len(state['current']): fail('current player list not empty although game has ended')
    except:
        fail('unexpected exception:\n' + traceback.format_exc())

    end.set()

for _ in range(2):
    threading.Thread(target=play, daemon=True).start()

end.wait()

if error:
    exit(1)
else:
    print('OK')
    exit(0)
