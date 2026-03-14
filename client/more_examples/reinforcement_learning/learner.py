#!/usr/bin/env python3
"""
Tic-tac-toe learner.

This client learns how to play tic-tac-toe using a method designed by Donald
Michie (see module menace). During training, a statistic is printed showing how
the performance develops over time.
"""

from game_server_api import GameServerAPI
from menace import MENACE

game = GameServerAPI(server='127.0.0.1', port=4711, game='TicTacToe', session='training', players=2)

batch_size = 1000 # learning progress will be printed after each batch of games
number_of_batches = 100

my_id = game.join()

menace = MENACE()
batches = 0
print('games,winrate,drawrate,sum')

while batches < number_of_batches:
    games = 0
    win = 0
    draw = 0

    # play a batch of games:
    while games < batch_size:
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
            win += 1
        elif winner is None:
            menace.draw()
            draw += 1
        else:
            menace.loss()

        # start new game:
        game.restart()
        games += 1

    # print training progress for the last batch of games:
    batches += 1
    winrate = win / games
    drawrate = draw / games
    games_total = batches * batch_size

    print(f'{games_total},{winrate:.3f},{drawrate:.3f},{winrate + drawrate:.3f}')
