#!/usr/bin/env python3
"""
Yahtzee client.

This program connects to the game server to play Yahtzee, alone, or against
other clients.
"""

from game_server_api import GameServerAPI, GameServerError, IllegalMove

game = GameServerAPI(server='127.0.0.1', port=4711, game='Yahtzee', token='mygame', players=1)

def print_scorecard(scorecard):
    print('\n' * 100)
    print('Yahtzee\n')
    for category, points in scorecard.items():
        points = str(points) if points is not None else ''
        print(f'{category:16s}{points:_>3s}')

def print_dice(dice):
    print('')
    for d in dice:
        print(f'[{d}] ', end='')
    print('\n a   b   c   d   e')

def menu(options, start=1):
    print('\nOptions:')
    for i, opt in enumerate(options, start):
        print(f'{i:3} - {opt}')
    while True:
        try:
            option = int(input('\nYour option: ')) - start
            if option < 0 or option >= len(options): raise ValueError
            return option
        except KeyboardInterrupt:
            print('')
            exit()
        except ValueError:
            print('Invalid option!')

def select_dice():
    selection = input('\nSelect one or more dice (e.g.: cde): ')
    indices = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4}
    dice = []
    for s in selection:
        dice.append(indices.get(s))
    return dice

def print_ranking(ranking):
    print('\nRanking:\n')
    ranking = list(ranking.items())
    ranking = sorted(ranking, key=lambda t: t[1], reverse=True)
    for name, points in ranking:
        print(f'{name:10s}{points:5}')

my_id = game.join()

# submit name:
while True:
    try:
        game.move(name=input('Enter name: '))
        break
    except IllegalMove as e:
        print(e)

categories = ['Ones', 'Twos', 'Threes', 'Fours', 'Fives', 'Sixes', 'Chance', 'Three of a Kind', 'Four of a Kind', 'Full House', 'Small Straight', 'Large Straight', 'Yahtzee']

state = game.state()

while not state['gameover']:
    print_scorecard(state['scorecard'])

    if my_id in state['current']: # my turn
        print_dice(state['dice'])

        option = menu(['roll all dice again', 'roll some dice again', 'add points to scorecard', 'cross out a category'])

        try:
            if option == 0:
                game.move(roll_dice=list(range(0, 5)))
            elif option == 1:
                game.move(roll_dice=select_dice())
            elif option == 2:
                cat = menu(categories)
                game.move(score='add points', category=categories[cat])
            elif option == 3:
                cat = menu(categories)
                game.move(score='cross out', category=categories[cat])
        except IllegalMove as e:
            print(e)
            input('\n<press enter>')
    else:
        if 'current_name' in state:
            print(f"\n{state['current_name']}'s turn ...")
        else:
            print('\nOpponents are choosing their names...')

    state = game.state()

print_scorecard(state['scorecard'])
print_ranking(state['ranking'])
