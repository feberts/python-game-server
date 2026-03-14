#!/usr/bin/env python3
"""
Tic-tac-toe opponent.

This client can be used in combination with the learner. It joins the game and
uses the same learning method.
"""

from game_server_api import GameServerAPI
from menace import MENACE

game = GameServerAPI(server='127.0.0.1', port=4711, game='TicTacToe', session='training')

my_id = game.join()

menace = MENACE()

while True:
    # play a single game:
    state = game.state()

    while not state['gameover']:
        if my_id in state['current']:
            pos = menace.move(state['board'])
            game.move(position=pos)

        state = game.state()

    # let menace know about the outcome:
    winner = state['winner']
    if winner == my_id:
        menace.win()
    elif winner is None:
        menace.draw()
    else:
        menace.loss()
