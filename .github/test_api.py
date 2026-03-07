#!/usr/bin/env python3
"""
Testing all API functions.
"""

from game_server_api import GameServerAPI, GameServerError, IllegalMove

SERVER = '127.0.0.1'
PORT = 4711

def fail(msg):
    exit(f'ERROR: {msg}')

# ========== join ==========

GAME = 'Echo'
TOKEN = 'test'
NAME = 'bob'

try:
    game_err = GameServerAPI(SERVER, PORT, 'InvalidGame', TOKEN, 1)
    my_id = game_err.join()
    fail('no exception when trying to start non-existent game')
except GameServerError:
    pass

try:
    game_err = GameServerAPI(SERVER, 9999, GAME, TOKEN, 1)
    my_id = game_err.join()
    fail('no exception despite invalid port')
except GameServerError:
    pass

try:
    game_err = GameServerAPI('127.0.0.13', PORT, GAME, TOKEN, 1)
    my_id = game_err.join()
    fail('no exception despite invalid ip')
except GameServerError:
    pass

try:
    game_err = GameServerAPI(SERVER, PORT, GAME, TOKEN)
    my_id = game_err.join()
    fail('no exception when trying to join non-existent session')
except GameServerError:
    pass

game = GameServerAPI(SERVER, PORT, GAME, TOKEN, 1, NAME)

try:
    game.move(msg='invalid')
    fail('no exception when performing move before game has started')
except GameServerError:
    pass

my_id = game.join()

try:
    game_err = GameServerAPI(SERVER, PORT, GAME, TOKEN)
    my_id = game_err.join()
    fail('no exception when trying to join full session')
except GameServerError:
    pass

# ========== move ==========

game.move(msg='hello')
state = game.state()

if state['echo'] != 'hello':
    fail('wrong echo after valid move')

try:
    game.move(invalid_key='hello')
    fail('no exception despite invalid key')
except IllegalMove:
    pass

try:
    game.move(msg='error')
    fail('no exception despite illegal move')
except IllegalMove:
    pass

state = game.state()
if state['echo'] != 'error':
    fail('wrong echo after sending error')

# ========== gameover ==========

if state['gameover']:
    fail('gameover although game has not ended')

game.move(msg='quit')
state = game.state()

if not state['gameover']:
    fail('no gameover despite quit')

try:
    game.move(msg='invalid')
    fail('no exception when performing move after game has ended')
except GameServerError:
    pass

# ========== restart ==========

game.restart()
state = game.state()

if state['echo'] != '':
    fail('wrong echo after restart')

if state['gameover']:
    fail('gameover after restart')

# ========== observe ==========

try:
    observer = GameServerAPI(SERVER, PORT, GAME, TOKEN, name='invalid')
    observer.observe()
    fail('observer: no exception despite invalid name')
except GameServerError:
    pass

observer = GameServerAPI(SERVER, PORT, GAME, TOKEN, name=NAME)
observer.observe()

game.move(msg='hello observer')
state = observer.state() # expecting state of old game before restart

if state['echo'] != 'quit':
    fail('observer: wrong echo in old game')

if not state['gameover']:
    fail('observer missed gameover')

state = observer.state() # expecting state of new game after restart

if state['echo'] != 'hello observer':
    fail('observer: wrong echo in new game')

if state['gameover']:
    fail('observer: wrong game status in new game')

try:
    observer.move(msg='invalid')
    fail('observer: no exception despite move')
except GameServerError:
    pass

try:
    observer.restart()
    fail('observer: no exception despite restart')
except GameServerError:
    pass

print('OK')
