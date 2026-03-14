#!/usr/bin/env python3
"""
Yahtzee client using the API wrapper.

This client program demonstrates the use of an API wrapper for Yahtzee.
Implementing wrapper functions is not necessary because the game server API is
generic and works with every game, but it can simplify the API usage.
"""

from yahtzee_api import YahtzeeAPI, GameServerError, IllegalMove

game = YahtzeeAPI(session='mygame', players=1)

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
        game.submit_name(input('Enter name: '))
        break
    except IllegalMove as e:
        print(e)

categories = ['Ones', 'Twos', 'Threes', 'Fours', 'Fives', 'Sixes', 'Chance', 'Three of a Kind', 'Four of a Kind', 'Full House', 'Small Straight', 'Large Straight', 'Yahtzee']

state = game.state()

while not state.gameover:
    print_scorecard(state.scorecard)

    if state.my_turn:
        print_dice(state.dice)

        option = menu(['roll all dice again', 'roll some dice again', 'add points to scorecard', 'cross out a category'])

        try:
            if option == 0:
                game.roll_all_dice()
            elif option == 1:
                game.roll_some_dice(select_dice())
            elif option == 2:
                cat = menu(categories)
                game.add_points(categories[cat])
            elif option == 3:
                cat = menu(categories)
                game.cross_out_category(categories[cat])
        except IllegalMove as e:
            print(e)
            input('\n<press enter>')
    else:
        if state.current_name:
            print(f"\n{state.current_name}'s turn ...")
        else:
            print('\nOpponents are choosing their names...')

    state = game.state()

print_scorecard(state.scorecard)
print_ranking(state.ranking)
