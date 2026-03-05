#!/usr/bin/env python3
"""
Tic-tac-toe client.

Run two clients to start a game.
"""

from game_server_api import GameServerAPI, GameServerError, IllegalMove

game = GameServerAPI(server='127.0.0.1', port=4711, game='TicTacToe', token='mygame', players=2)

symbols = ('x', 'o')

def print_board(board):
    print('\n' * 100)
    board = [i + 1 if board[i] == -1 else symbols[board[i]] for i in range(9)]
    print(f' {board[0]} | {board[1]} | {board[2]}', '---+---+---',
          f' {board[3]} | {board[4]} | {board[5]}', '---+---+---',
          f' {board[6]} | {board[7]} | {board[8]}', sep='\n')

def user_input(prompt):
    while True:
        try:
            return int(input(prompt)) - 1
        except KeyboardInterrupt:
            print('')
            exit()
        except ValueError:
            print('Integers only!')

print('waiting for another player to join ...')

my_id = game.join()
state = game.state()

while not state['gameover']:
    print_board(state['board'])

    if my_id in state['current']: # my turn
        while True:
            pos = user_input(f'\nPlayer {symbols[my_id]}, your turn: ')

            try:
                game.move(position=pos)
                break
            except IllegalMove as e:
                print(e)
    else:
        print("Opponent's turn ...")

    state = game.state()

print_board(state['board'])
winner = state['winner']

if winner is None:
    print('No winner...')
elif winner == my_id:
    print(f'You win!')
else:
    print(f'You lose...')
