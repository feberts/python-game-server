#!/usr/bin/env python3
"""
Tic-tac-toe client using the API wrapper.

This client program demonstrates the use of an API wrapper for tic-tac-toe.
Implementing wrapper functions is not necessary because the game server API is
generic and works with every game, but it can simplify the API usage.
"""

from tictactoe_api import TicTacToeAPI, GameServerError, IllegalMove

game = TicTacToeAPI(session='mygame')

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

my_id = game.join()
state = game.state()

while not state.gameover:
    print_board(state.board)

    if state.my_turn:
        while True:
            pos = user_input(f'\nPlayer {symbols[my_id]}, your turn: ')

            try:
                game.put_mark(pos)
                break
            except IllegalMove as e:
                print(e)
    else:
        print("Opponent's turn ...")

    state = game.state()

print_board(state.board)

if state.winner is None:
    print('No winner...')
elif state.winner:
    print('You win!')
else:
    print('You lose...')
