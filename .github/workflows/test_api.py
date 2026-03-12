#!/usr/bin/env python3
"""
Testing all API functions.
"""

from game_server_api import GameServerAPI, GameServerError, IllegalMove

import threading

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

# ========== auto-join ==========

GAME = 'Chat'
player1 = None

def join_game():
    global player1
    player1 = GameServerAPI(SERVER, PORT, GAME, 'auto', 2)
    player1.join()

t = threading.Thread(target=join_game, daemon=True)
t.start()
player2 = GameServerAPI(SERVER, PORT, GAME, players=2)
player2.join()
t.join()
player1.move(name='player1')
player2.move(name='player2')

player1.move(message='Hello player2')
state = player2.state()
name, msg = state['messages'][0]
if name != 'player1' or msg != 'Hello player2':
    fail('wrong state in auto-join session')

try:
    other = GameServerAPI(SERVER, PORT, GAME)
    other.join()
    fail('auto-join: no exception despite missing number of players')
except GameServerError:
    pass

other = GameServerAPI(SERVER, PORT, GAME, players=1)
other.join()
other.move(name='other')
other.move(message='other message')

state = player1.state()
name, msg = state['messages'][-1]
if name != 'player1' or msg != 'Hello player2':
    fail('interfering auto-join sessions')

print('OK')
