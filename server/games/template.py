"""
Template for new games.

This file can be used as a template for new games. Just follow these steps:

  1. Change the name of this file to something more descriptive.
  2. Name class MyNewGame after your game. Clients will use that name to
     start a game.
  3. Implement all the methods.
  4. Add the class to the list of games in server/games_list.py.
  5. Implement a client or help others to implement clients by writing
     documentation for the new game.

That's it. For orientation, you can also take a look at the implementations of
the other games.
"""

from abstract_game import AbstractGame

class MyNewGame(AbstractGame): # TODO pick a proper name
    """
    Base class for games.

    This class serves as a base class for games. Every new game must be derived
    from this class and implement all its methods. These methods will be called
    by the framework. Furthermore, every new game must be added to the list of
    available games.

    In some cases, the framework performs checks before it calls a method. In
    such a case, it can be assumed, that the argument passed is valid. Refer to
    the method descriptions to see which parameters this may apply to.

    None of the methods may raise exceptions. If this happens anyway, the
    framework will catch the exception to prevent the server from crashing, log
    this event and report a generic error message back to the client.
    """

    def __init__(self, players):
        """
        Constructor.

        The framework assigns IDs in the range 0...n-1 to all players that join
        a game. It then passes the total number of players to this constructor.
        The framework makes sure that only a defined number of players can join
        the game. The number of allowed players is specified by functions
        min_players and max_players. The desired number of players is provided
        by the client starting a new game.

        Parameters:
        players (int): number of players (no parameter check required)
        """
        raise NotImplementedError
        # TODO use the constructor to initialize attributes, if needed

    @staticmethod
    def min_players():
        """
        Returns the minimum number of players.

        This function reports the minimum number of players required to play the
        game to the framework.

        Returns:
        int: minimum number of players
        """
        raise NotImplementedError
        # TODO return the minimum number of players

    @staticmethod
    def max_players():
        """
        Returns the maximum number of players.

        This function reports the maximum number of players allowed in the game
        to the framework.

        Returns:
        int: maximum number of players
        """
        raise NotImplementedError
        # TODO return the maximum number of players

    def current_player(self):
        """
        Returns a list of players who can currently submit a move.

        A game class must keep track of which player must perform the next move.
        This can be a single player, multiple players, or no player at all. This
        function reports the corresponding player IDs to the framework. In
        return, the framework makes sure, that no other players can submit a
        move.

        Returns:
        list: player IDs
        """
        raise NotImplementedError
        # TODO return a list (!) of player IDs

    def move(self, move, player_id):
        """
        Handle a move.

        A player's move is passed as a dictionary. The content of this
        dictionary entirely depends on the needs of the game. The API function
        to submit a move on the client side accepts the data as keyword
        arguments (**kwargs). Those keyword arguments are then converted to a
        dictionary and sent to the server. It is important to let the user of
        the API know about the names of these keywords and the expected data
        types of their values. The use of kwargs in the API function allows for
        a maximum of flexibility. This way there are no limitations concerning
        player moves. An unlimited number of different moves of any complexity
        is possible.

        The framework makes sure, that only the current player(s) can submit a
        move. The framework also guaranties, that the argument is of type
        dictionary, but the validity of the contained data must be checked
        thoroughly by the implementer of the game class.

        Error handling:

        In order to respond to illegal moves, error messages must be returned.
        These are then sent back to the client, where the corresponding API
        function raises an exception containing the message. If a move is legal,
        None must be returned.

        Instead of returning a string, any object that is compatible with JSON
        can be returned, including a tuple. For example, a tuple containing both
        a message and an error code could be returned. In the case of a tuple,
        all elements are passed to the raised exception as individual arguments.
        It is important to let the API user know about the structure of the
        error object.

        Parameters:
        move (dict): the player's move (must be checked)
        player_id (int): ID of the player submitting the move (no parameter check required)

        Returns:
        error message in case the move is illegal, None otherwise (see above for details)
        """
        raise NotImplementedError
        # TODO return a message in case of an illegal move, or None otherwise

    def game_over(self):
        """
        Returns the game status.

        A boolean value is returned indicating whether the game has ended or is
        still active. After the game has ended, the framework makes sure that
        moves can no longer be submitted. Clients will still be able to retrieve
        the game state after the game has ended.

        Returns:
        bool: True, if game has ended, else False
        """
        raise NotImplementedError
        # TODO return True/False

    def state(self, player_id):
        """
        Returns the game state as a dictionary.

        This can be the complete state of the game, or just specific information
        for a specific player. What information is returned depends entirely on
        the game. In some games all information is available to all players, in
        other games players can possess information that is hidden from the
        others.

        It is important to let the user of the API know how the dictionary is
        structured, so its content can be accessed properly.

        The framework will add additional data to the state after it is returned
        by this function. The following information is added:

        - the current player's ID as returned by function current_player; the
          framework will add it automatically as the value to a key named
          'current'; this way, all players are aware of who's turn it is
        - a boolean value as returned by function game_over indicating whether
          the game has ended or is still active; the framework will add it
          automatically as the value to a key named 'gameover'

        Parameters:
        player_id (int): ID of the player requesting the state (no parameter check required)

        Returns:
        dict: game state
        """
        raise NotImplementedError
        # TODO return a dictionary containing the game state
