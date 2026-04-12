"""
Tic-tac-toe game.

This module provides a tic-tac-toe implementation.
"""

import random

from abstract_game import AbstractGame

class TicTacToe(AbstractGame):
    """
    Class TicTacToe.

    This class implements a tic-tac-toe game.
    """

    class _State:
        def __init__(self):
            self.board = [-1] * 9
            self.current = random.randint(0, 1)
            self.gameover = False
            self.winner = None

    def __init__(self, players): # override
        """
        Constructor.

        Parameters:
        players (int): number of players (unused)
        """
        self._state = self._State()

    def state(self, player_id): # override
        """
        Returns the game state as a dictionary.

        Dictionary content:
        'board': integer list of size 9, values: -1 for empty cells, 0 or 1 for player marks
        'winner': player ID, or None if there is no winner

        Parameters:
        player_id (int): player ID (unused)

        Returns:
        dict: game state
        """
        return {'board':self._state.board, 'winner':self._state.winner}

    def move(self, move, player_id): # override
        """
        Submit a move.

        The move is passed as a dictionary containing the key 'position' with a
        board position (0-8) as its value.

        Parameters:
        move (dict): the current player's move
        player_id (int): player ID (unused)

        Returns:
        str: error message in case the move was illegal, None otherwise
        """
        if 'position' not in move:
            return "keyword argument 'position' of type int missing"
        if type(move['position']) != int:
            return "type of argument 'position' must be int"

        pos = int(move['position'])
        err = self._check_move(pos)
        if err: return err

        self._update_board(pos)
        self._check_win()
        self._check_board_full()
        self._state.current ^= 1 # rotate players

        return None

    def _check_move(self, pos):
        """
        Check if a move is legal.
        """
        if pos < 0 or pos > 8:
            return 'invalid position'
        if self._state.board[pos] != -1:
            return 'position already occupied'

        return None

    def _update_board(self, pos):
        """
        Add current player's mark to the board.
        """
        self._state.board[pos] = self._state.current

    def _check_win(self):
        """
        Check if the current player has won.
        """
        b = self._state.board
        for i, j, k in ((0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)):
            if b[i] == b[j] == b[k] == self._state.current:
                self._state.winner = self._state.current
                self._state.gameover = True
                return

    def _check_board_full(self):
        """
        Check if the board is filled completely.
        """
        if -1 not in self._state.board:
            self._state.gameover = True

    def current_player(self): # override
        return [self._state.current]

    def game_over(self): # override
        return self._state.gameover

    @staticmethod
    def min_players(): # override
        return 2

    @staticmethod
    def max_players(): # override
        return 2
