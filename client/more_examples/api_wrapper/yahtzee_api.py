"""
Yahtzee API wrapper.

This is a demonstration of how one could implement an API with wrapper functions
for a specific game. Doing this is not necessary, because the game server API is
generic and works with every game, but it can simplify the API usage.
"""

from game_server_api import GameServerAPI, GameServerError, IllegalMove

class YahtzeeAPI:
    """
    Class YahtzeeAPI.

    This class provides API wrapper functions for Yahtzee.
    """

    def __init__(self, session, players, name=''):
        self._api = GameServerAPI('127.0.0.1', 4711, 'Yahtzee', session, players, name)
        self.my_id = None

    def join(self):
        self.my_id = self._api.join()
        return self.my_id

    def submit_name(self, name):
        self._api.move(name=name)

    def roll_all_dice(self):
        self._api.move(roll_dice=list(range(0, 5)))

    def roll_some_dice(self, dice):
        self._api.move(roll_dice=dice)

    def add_points(self, category):
        self._api.move(score='add points', category=category)

    def cross_out_category(self, category):
        self._api.move(score='cross out', category=category)

    def state(self):
        state = self._api.state()
        return State(state, self.my_id)

class State:
    """
    Class State.

    Usually, a dictionary is returned by the state function. Here, all data is
    encapsulated in a class for easy access.
    """

    def __init__(self, state, my_id):
        gameover = state['gameover']
        self.my_turn = my_id in state['current']
        self.gameover = gameover
        self.scorecard = state['scorecard']
        self.dice = state['dice'] if not gameover else None
        self.current_name = state['current_name'] if 'current_name' in state else None
        self.ranking = state['ranking'] if gameover else None
