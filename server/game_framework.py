"""
Game framework.

This module implements the game framework. The framework is responsible for
managing active game sessions. Client requests are parsed, and the appropriate
actions are performed. The following requests can be handled by the framework:

- starting and joining a game session
- submitting a move
- requesting the game state
- observing a player
- restarting a game

To perform these actions, the framework calls the methods of the corresponding
game class instance, if necessary.
"""

import threading
import time

import config
import games_list
import game_session
import utility

log = utility.FrameworkLogger()

class GameFramework:
    """
    Class GameFramework.

    This class manages active game sessions and handles the interaction between
    clients and game instances.
    """

    def __init__(self):
        self._game_classes = {} # game name -> game class
        self._game_sessions = {} # (game name, token) -> game session
        self._handlers = {
            'join':self._join,
            'move':self._move,
            'state':self._state,
            'observe':self._observe,
            'restart':self._restart}
        self._build_game_class_dict()
        self._start_clean_up()
        self._player_joins = threading.Event()
        self._auto_join_tokens = {} # game name -> auto-join token
        self._next_auto_join_token = 0
        self._AUTO = 'auto'
        self._lock = threading.Lock()

    def _build_game_class_dict(self):
        """
        Build a dictionary mapping game names to game classes.
        """
        for game_class in games_list.games:
            self._game_classes[game_class.__name__] = game_class

    def handle_request(self, request):
        """
        Handling a client request.

        This function is called by the server. It identifies the type of the
        request and redirects it to the corresponding method. The returned data
        is handed back to the server and then sent to the client.

        Parameters:
        request (dict): client request

        Returns:
        dict: reply
        """
        if 'type' not in request:
            return utility.framework_error('no request type specified')
        if request['type'] not in self._handlers:
            return utility.framework_error('invalid request type')

        log.request(request)
        response = self._handlers[request['type']](request)
        log.response(response)

        return response

    def _join(self, request):
        """
        Request handler for starting and joining a game session.

        This function first checks if a game session specified by the game's
        name and the token is already created and still waiting for clients to
        join. If this is the case, the request is passed to the function for
        joining a session. In all other cases, the function for starting a new
        game session is called. This implies that an already running session
        will be terminated. When a client makes use of the auto-join
        functionality, a unique token is generated. In this case, sessions are
        never terminated. A new session is created instead.

        Parameters:
        request (dict): request containing game name and token

        Returns:
        dict: containing the player's ID and key
        """
        # check and parse request:
        err = utility.check_dict(request, {
            'game':str, 'session':str, 'players':(int, type(None)), 'name':str})
        if err: return utility.framework_error(err)

        game_name = request['game']
        token = request['session']
        players = request['players']
        name = request['name']

        if game_name not in self._game_classes:
            return utility.framework_error('no such game')

        if token.startswith(self._AUTO) and len(token) > len(self._AUTO):
            return utility.framework_error("token must not start with reserved prefix 'auto'")

        # generate token for auto-joining clients:
        if token == self._AUTO:
            token = self._generate_auto_join_token(game_name, players)
            name = '' # no observer mode for auto-join sessions

        # retrieve game session, if it exists:
        session, _ = self._retrieve_session(game_name, token)

        # start or join a session:
        if session and not session.full():
            return self._join_session(session, name, token)
        elif not session and not players:
            return utility.framework_error(
                'no such game session; provide the number of players to start one')
        elif session and session.full() and not players:
            return utility.framework_error('game session already full')
        else:
            return self._start_session(game_name, token, players, name)

    def _start_session(self, game_name, token, players, name):
        """
        Starting a game session.

        This function instantiates the requested game and adds it to the list of
        active game sessions. After the required number of players has joined
        the game, the function sends the player ID back to the client who
        requested the start of the game. If not enough players have joined the
        game before the timeout occurs, the game session is deleted and the
        requesting client is informed. A repeated call of this function will end
        an active game session and start a new one, which the other players will
        have to join again.

        In addition to the ID, a unique key is generated for the player and sent
        to the client. It is automatically included in every future request sent
        by the client and then checked by the framework to prevent cheating.

        Parameters:
        game_name (str): name of the game
        token (str): name of the game session
        players (int): total number of players
        name (str): player name, can be an empty string

        Returns:
        dict: containing the player's ID and key
        """
        # check number of players:
        game_class = self._game_classes[game_name]

        if players > game_class.max_players() or players < game_class.min_players():
            return utility.framework_error('invalid number of players')

        # retrieve old game session, if it exists, and notify clients:
        old_session, _ = self._retrieve_session(game_name, token)

        if old_session:
            old_session.mark_overwritten()
            old_session.wake_up_threads()

        # create game session and add it to dictionary of active sessions:
        session = game_session.GameSession(game_class, players)
        self._game_sessions[(game_name, token)] = session

        # get player ID and key:
        player_id, key, _ = session.next_id(name)

        # wait for others to join:
        self._await_game_start(session)
        self._remove_auto_join_token(game_name, token)

        if not session.full(): # timeout reached
            if (game_name, token) in self._game_sessions:
                del self._game_sessions[(game_name, token)]
            return utility.framework_error('timeout while waiting for others to join')

        log.info(f'Starting session {game_name}:{token}')

        return self._return_data({
            'player_id':player_id,
            'key':key,
            'session':token,
            'request_size_max':config.request_size_max})

    def _join_session(self, session, name, token):
        """
        Joining a game session.

        This function lets a client join an existing game session. After the
        required number of players has joined the game, the function sends the
        player ID back to the client who requested to join the game. If not
        enough players have joined the game before the timeout occurs, the
        requesting client is informed.

        In addition to the ID, a unique key is generated for the player and sent
        to the client. It is automatically included in every future request sent
        by the client and then checked by the framework to prevent cheating.

        Parameters:
        session (GameSession): game session
        name (str): player name, can be an empty string
        token (str): name of the game session

        Returns:
        dict: containing the player's ID and key
        """
        # get player ID and key:
        player_id, key, err = session.next_id(name)
        if err: return utility.framework_error(err)

        # wait for others to join:
        self._player_joins.set()
        self._await_game_start(session)

        if not session.full(): # timeout reached
            return utility.framework_error('timeout while waiting for others to join')

        return self._return_data({
            'player_id':player_id,
            'key':key,
            'session':token,
            'request_size_max':config.request_size_max})

    def _move(self, request):
        """
        Request handler for player moves.

        This function handles a client's move. It makes sure that it is the
        client's turn to submit a move. It then passes the move to the game
        session and returns the game session's message in case of an invalid
        move.

        Parameters:
        request (dict): containing information about the game session and the player's move

        Returns:
        dict: containing information in case of an invalid move
        """
        # check and parse request:
        err = utility.check_dict(request, {
            'game':str, 'session':str, 'player_id':int, 'key':str, 'move':dict})
        if err: return utility.framework_error(err)

        game_name = request['game']
        token = request['session']
        player_id = request['player_id']
        key = request['key']
        move = request['move']

        # retrieve the game session:
        session, err = self._retrieve_session(game_name, token)
        if err: # no such game or game session
            return err

        # check if game is still active:
        if session.game_over():
            return utility.framework_error('game has ended')

        # check if key and ID match:
        if not session.key_valid(player_id, key):
            return utility.framework_error('invalid key')

        # check if it is the client's turn:
        if player_id not in session.current_player():
            return utility.framework_error('not your turn')

        # pass the move to the game session:
        err = session.game_move(move, player_id)
        if err: return utility.game_error(err)

        return self._return_data(None)

    def _state(self, request):
        """
        Request handler for game state requests.

        This function retrieves the game state from a game session and sends it
        back to the client.

        Parameters:
        request (dict): containing information about the game session and the player

        Returns:
        dict: containing the game state
        """
        # check and parse request:
        err = utility.check_dict(request, {
            'game':str, 'session':str, 'player_id':int, 'key':str, 'observer':bool})
        if err: return utility.framework_error(err)

        game_name = request['game']
        token = request['session']
        player_id = request['player_id']
        key = request['key']
        observer = request['observer']

        # retrieve the game session:
        session, err = self._retrieve_session(game_name, token)
        if err: # no such game or game session
            return err

        # check if key and ID match:
        if not session.key_valid(player_id, key):
            return utility.framework_error('invalid key')

        # retrieve the game state:
        state = session.game_state(player_id, observer)

        # check if session was overwritten while clients are waiting for state change:
        if session.overwritten():
            return utility.framework_error('game session was overwritten')

        # check if session has timed out while clients are waiting for state change:
        if session.timed_out():
            return utility.framework_error('game session has timed out')

        return self._return_data(state)

    def _observe(self, request):
        """
        Request handler for observing another player.

        To observe another player in the same game session, the observing client
        needs to know the ID of that player. This function retrieves that ID
        based on the player's name. This only works, if the player has supplied
        a name when joining the game session. The observed player's key is sent
        to the client as well. The observer mode is not available for auto-join
        sessions.

        Parameters:
        request (dict): request containing game name, token and player to be observed

        Returns:
        dict: containing the ID of the observed player
        """
        # check and parse request:
        err = utility.check_dict(request, {'game':str, 'session':str, 'name':str})
        if err: return utility.framework_error(err)

        game_name = request['game']
        token = request['session']
        player_name = request['name']

        if token == self._AUTO:
            return utility.framework_error('observer mode not available for auto-join sessions')

        # retrieve game session:
        session, err = self._retrieve_session(game_name, token)
        if err: # no such game or game session
            return err
        if not session.full(): # game has not yet started
            return utility.framework_error('game has not yet started')

        # get player ID and key:
        player_id, key, err = session.get_id(player_name)
        if err: return utility.framework_error(err)

        return self._return_data({'player_id':player_id, 'key':key})

    def _restart(self, request):
        """
        Request handler for restarting a game.

        This function restarts a game. The game class object is replaced with a
        new one, the game session itself stays untouched. There is no need to
        rejoin the game, and all players will keep their IDs. This is useful
        when simulating many games to collect data for AI training.

        Parameters:
        request (dict): containing information about the game session

        Returns:
        dict: containing an error message, if the request is invalid
        """
        # check and parse request:
        err = utility.check_dict(request, {
            'game':str, 'session':str, 'player_id':int, 'key':str})
        if err: return utility.framework_error(err)

        game_name = request['game']
        token = request['session']
        player_id = request['player_id']
        key = request['key']

        # retrieve the game session:
        session, err = self._retrieve_session(game_name, token)
        if err: # no such game or game session
            return err

        # check if key and ID match:
        if not session.key_valid(player_id, key):
            return utility.framework_error('invalid key')

        # restart game:
        session.restart_game(player_id)

        return self._return_data(None)

    def _await_game_start(self, session):
        """
        Waits for players to join the game.

        This function waits until the required number of players has joined the
        game or until the timeout is reached.

        Parameters:
        session (GameSession): game session
        """
        start = session.last_access()

        while not session.full() and time.time() - start < config.game_timeout:
            self._player_joins.clear()
            self._player_joins.wait(config.game_timeout)

    def _retrieve_session(self, game_name, token):
        """
        Retrieves an active game session.

        If the specified game session exists, it is returned.

        Parameters:
        game_name (str): game name
        token (str): token

        Returns:
        tuple(GameSession, dict):
            GameSession: game session, None in case of an error
            dict: error message, if a problem occurred, None otherwise
        """
        # check if game session exists:
        if game_name not in self._game_classes:
            return None, utility.framework_error('no such game')
        if (game_name, token) not in self._game_sessions:
            return None, utility.framework_error('no such game session')

        return self._game_sessions[(game_name, token)], None

    def _generate_auto_join_token(self, game_name, players):
        """
        Generate a unique token for an auto-join session.

        Parameters:
        game_name (str): name of the game
        players (int): total number of players

        Returns:
        str: a unique token for an auto-join session, None in case of an error
        """
        with self._lock:
            if game_name not in self._auto_join_tokens:
                if not players: return None
                token = f'{self._AUTO}-{self._next_auto_join_token}'
                self._next_auto_join_token += 1
                self._auto_join_tokens[game_name] = token
            else:
                token = self._auto_join_tokens[game_name]

            return token

    def _remove_auto_join_token(self, game_name, token):
        """
        This function is used to remove a token from the auto-join dictionary
        after the session has been started.

        Parameters:
        game_name (str): name of the game
        token (str): name of the game session
        """
        if token.startswith(self._AUTO):
            del self._auto_join_tokens[game_name]

    def _return_data(self, data):
        """
        Adds data to a dictionary to be sent back to the client. This function
        is to be used only for sending regular data back to a client as a
        response to a valid request. It must not be used for sending error
        messages (hence the status flag 'ok').
        """
        return {'status':'ok', 'data':data}

    def _start_clean_up(self):
        """
        Starting the clean up function in a separate thread.
        """
        threading.Thread(target=self._clean_up, args=(), daemon=True).start()

    def _clean_up(self):
        """
        Deleting inactive game sessions after a defined time span without read
        or write access.
        """
        while True:
            time.sleep(config.game_timeout)

            # mark sessions for deletion:
            old_sessions = []
            for (game_name, token), session in self._game_sessions.items():
                if session.last_access() + config.game_timeout < time.time():
                    old_sessions.append((game_name, token))

            # delete old sessions:
            for (game_name, token) in old_sessions:
                session = self._game_sessions[(game_name, token)]
                session.mark_timed_out()
                session.wake_up_threads()
                del self._game_sessions[(game_name, token)]
                log.info(f'Deleting session {game_name}:{token}')
