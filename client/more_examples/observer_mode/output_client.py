#!/usr/bin/env python3
"""
Tic-tac-toe output client.

This program joins a game session as a passive observer. It can be used in
combination with the input client (as well as with a regular client). The input
client joins a session as an active player and submits moves. This way, the
implementation of input and output can be divided between two programs. Both
programs need to pass the same value for the name parameter when joining a game
session.
"""

from game_server_api import GameServerAPI, GameServerError, IllegalMove

game = GameServerAPI(server='127.0.0.1', port=4711, game='TicTacToe', token='mygame', name='bob')

symbols = ('x', 'o')

def print_board(board):
    print('\n' * 100)
    board = [i + 1 if board[i] == -1 else symbols[board[i]] for i in range(9)]
    print(f' {board[0]} | {board[1]} | {board[2]}', '---+---+---',
          f' {board[3]} | {board[4]} | {board[5]}', '---+---+---',
          f' {board[6]} | {board[7]} | {board[8]}', sep='\n')

observed_id = game.observe()
state = game.state()

while not state['gameover']:
    print_board(state['board'])

    if observed_id in state['current']: # my turn
        print(f'Player {symbols[observed_id]}, your turn!')
    else:
        print("Opponent's turn ...")

    state = game.state()

print_board(state['board'])
winner = state['winner']

if winner is None:
    print('No winner...')
elif winner == observed_id:
    print('You win!')
else:
    print('You lose...')
