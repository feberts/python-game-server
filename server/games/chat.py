"""
Chat.

This module provides a chat that allows clients to exchange messages.
"""

from abstract_game import AbstractGame

class Chat(AbstractGame):
    def __init__(self, players):
        self._messages = [] # (name, message)
        self._names = {} # ID -> name
        self._players = players

    @staticmethod
    def min_players():
        return 1

    @staticmethod
    def max_players():
        return 100

    def current_player(self):
        return list(range(self._players))

    def move(self, move, player_id):
        if 'name' in move:
            name = move['name'].strip()
            if name in self._names.values():
                return 'name already in use'
            if name == '':
                return 'name must not be an empty string'
            self._names[player_id] = name

        if 'message' in move:
            if player_id not in self._names:
                return 'you must submit your name first'
            message = move['message'].strip()
            if message == '':
                return None
            self._messages.append((self._names[player_id], message))

    def game_over(self):
        return False

    def state(self, player_id):
        return {'messages': self._messages}
