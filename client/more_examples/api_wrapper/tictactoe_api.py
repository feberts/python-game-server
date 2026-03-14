"""
Tic-tac-toe API wrapper.

This is a demonstration of how one could implement an API with wrapper functions
for a specific game. Doing this is not necessary, because the game server API is
generic and works with every game, but it can simplify the API usage.
"""

from game_server_api import GameServerAPI, GameServerError, IllegalMove

class TicTacToeAPI:
    """
    Class TicTacToeAPI.

    This class provides API wrapper functions for tic-tac-toe.
    """

    def __init__(self, session, name=''):
        self._api = GameServerAPI('127.0.0.1', 4711, 'TicTacToe', session, 2, name)
        self.my_id = None

    def join(self):
        self.my_id = self._api.join()
        return self.my_id

    def put_mark(self, position):
        self._api.move(position=position)

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
        self.my_turn = my_id in state['current']
        self.board = state['board']
        self.gameover = state['gameover']
        self.winner = None if state['winner'] is None else state['winner'] == my_id
