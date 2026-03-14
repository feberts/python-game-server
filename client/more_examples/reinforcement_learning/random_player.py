#!/usr/bin/env python3
"""
Tic-tac-toe random player.

This client joins a game and submits random (but legal) moves. It is used in
combination with the learning client to produce data for AI training.
"""

import random

from game_server_api import GameServerAPI

game = GameServerAPI(server='127.0.0.1', port=4711, game='TicTacToe', session='training')

def random_move(board):
    vacant = [i for i in range(9) if board[i] == -1]
    return random.choice(vacant)

my_id = game.join()

while True:
    state = game.state()

    if my_id in state['current']:
        pos = random_move(state['board'])
        game.move(position=pos)
