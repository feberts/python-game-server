#!/usr/bin/env python3
"""
Testing TLS.
"""

from game_server_api import GameServerAPI, GameServerError

SERVER = 'localhost'
PORT = 4711

def fail(msg):
    exit(f'ERROR: {msg}')

# ========== encryption only ==========

game = GameServerAPI(SERVER, PORT, 'Echo', 'tlstest', 1)

try:
    game.enable_tls()

    game.join()
    game.move(msg='Hello')
    state = game.state()
    if state['echo'] != 'Hello':
        fail('wrong echo')
except GameServerError as e:
    fail(e)

# ========== encryption and server identity verification ==========

game = GameServerAPI(SERVER, PORT, 'Echo', 'tlstest', 1)

try:
    game.enable_tls('cert.pem')

    game.join()
    game.move(msg='Hello')
    state = game.state()
    if state['echo'] != 'Hello':
        fail('wrong echo')
except GameServerError as e:
    fail(e)

print('OK')
