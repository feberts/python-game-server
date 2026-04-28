"""
A lightweight server and framework for turn-based multiplayer games.
Copyright (C) 2025, 2026 Fabian Eberts

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

"""
Game server API.

This module provides an API for communicating with the game server. The API can
be used to

- start or join a game session
- submit moves to the server
- retrieve the game state
- passively observe a specific player
- restart a game within the current session
- enable TLS
"""

import json
import os
import socket
import ssl
import traceback

class GameServerError(Exception): pass
class IllegalMove(Exception): pass

class GameServerAPI:
    """
    Class GameServerAPI.

    This class provides API functions to communicate with the game server.
    """

    def __init__(self, server, port, game, session='auto', players=None, name=''):
        """
        Information needed in order to connect to the server and to start or
        join a game session is passed to this constructor. Parameter game
        specifies the game to be started. It corresponds to the name of the game
        class on the server. To be able to join a specific game session, all
        participants need to agree on a session token and pass it to the
        constructor. The token is used to identify the game session.
        Alternatively, you can have the server automatically assign you to a
        session by passing 'auto' as the token (this is the default). Refer to
        function join for more information.

        The optional parameter players is required by function join in order to
        start a new game session with the specified number of players. If the
        argument is omitted, the join function will only try to join an existing
        session but never start a new one. The argument is ignored when an
        existing session can be joined.

        The optional parameter name makes it possible for other clients to
        passively observe your playing by joining a game using the observe
        function. They will receive the same data calling the state function as
        you do.

        Parameters:
        server (str): IP or hostname
        port (int): port number
        game (str): name of the game
        session (str): name of the game session (optional), 'auto' for auto-join (default)
        players (int): total number of players (optional)
        name (str): player name (optional)

        Raises:
        AssertionError: for invalid arguments
        """
        assert type(server) == str and len(server) > 0, self._error('server')
        assert type(port) == int and 0 <= port <= 65535, self._error('port')
        assert type(game) == str and len(game) > 0, self._error('game')
        assert type(session) == str and len(session) > 0, self._error('session')
        assert players is None or type(players) == int and players > 0, self._error('players')
        assert type(name) == str, self._error('name')

        # server:
        self._server = server
        self._port = port

        # game session:
        self._game = game
        self._session = session
        self._players = players
        self._name = name
        self._player_id = None
        self._key = None
        self._observer = False

        # tcp connections:
        self._buffer_size = 4096 # bytes, corresponds to server-side buffer size
        self._request_size_max = int(1e6) # bytes, updated after joining a game
        self._tls_context = None

    def join(self):
        """
        Start or join a game session.

        This function lets a client join a game session. A new session is
        started, if necessary. In order to start a new session, the number of
        players must be passed to the constructor. If the argument is omitted,
        this function will only try to join an existing session but never start
        a new one. The argument is ignored when an existing session can be
        joined.

        There are two ways to start or join a game session:

        - By providing a shared session token to the constructor. All clients
          using the same token will join this specific game session. If such a
          session exists but is already fully occupied by players, it is
          terminated and a new session is started.
        - By passing the string 'auto' as the session token. This causes the
          server to automatically assign you to an open session. If no session
          exists that can be joined, a new one is started. Existing sessions are
          never terminated. This method of starting and joining sessions does
          not interfere with the above method. To achieve this, the server
          creates a unique token internally.

        The game starts as soon as the required number of clients has joined the
        game. The function then returns the player ID. The server assigns IDs in
        the range 0...n-1 to all players that join the game.

        Returns:
        int: player ID

        Raises:
        GameServerError: in case no session could be started or joined
        """
        response, err, _ = self._send({
            'type':'join',
            'game':self._game,
            'session':self._session,
            'players':self._players,
            'name':self._name})

        if err: raise GameServerError(err)

        self._player_id = response['player_id']
        self._key = response['key']
        self._session = response['session']
        self._request_size_max = response['request_size_max']

        return self._player_id

    def move(self, **move):
        """
        Submit a move.

        This function is used to submit a move to the game server. The move must
        be passed as keyword arguments. Refer to the documentation of a specific
        game to find out about the required or available arguments. If it is not
        your turn to submit a move or if the move is illegal, the server replies
        with an error message, and an exception containing the message is
        raised. The message can be any object compatible with JSON. Refer to the
        documentation of a specific game for more information about error
        handling.

        Parameters:
        move (keyword arguments): the player's move

        Raises:
        IllegalMove: in case of an illegal move
        GameServerError: in case any other error occurred
        """
        if self._player_id is None: raise GameServerError('join a game first')
        if self._observer: raise GameServerError('cannot submit moves as observer')

        _, err, status = self._send({
            'type':'move',
            'game':self._game,
            'session':self._session,
            'player_id':self._player_id,
            'key':self._key,
            'move':move})

        if err:
            if status == 'illegalmove':
                if type(err) == list:
                    raise IllegalMove(*err)
                else:
                    raise IllegalMove(err)
            else:
                raise GameServerError(err)

    def state(self):
        """
        Retrieve the game state.

        This function retrieves the game state from the server. The state is
        returned as a dictionary. Refer to the documentation of a specific game
        to find out about the structure and content of the dictionary.

        Independent of the game, the dictionary always contains these two keys:

        - 'current': a list of player IDs, indicating whose player's turn it is
        - 'gameover': a boolean value indicating whether the game has ended or
          is still active

        This function will block until the game state changes. Only then will
        the server respond with the updated state. This is more efficient than
        polling. To avoid deadlocks, the function never blocks in these
        situations:

        - when the game has just started to allow clients to get the initial
          state
        - after a move was performed to allow clients to get the new state
        - when the game was restarted and a client still has to get the previous
          game's state

        Returns:
        dict: game state

        Raises:
        GameServerError: in case the state could not be retrieved
        """
        if self._player_id is None: raise GameServerError('join a game first')

        state, err, _ = self._send({
            'type':'state',
            'game':self._game,
            'session':self._session,
            'player_id':self._player_id,
            'key':self._key,
            'observer':self._observer})

        if err: raise GameServerError(err)

        return state

    def observe(self):
        """
        Observe another player.

        This function lets one client observe another client. The name of the
        player to be observed must be passed to the constructor. You will then
        receive the same data calling the state function as that player does.
        This function will return the player ID of the observed player.

        This function can only be called, after the specified game session has
        already been started. The observer mode is not available for auto-join
        sessions.

        Returns:
        int: ID of the observed player

        Raises:
        GameServerError: in case the session could not be joined as observer
        """
        if type(self._name) != str or len(self._name) == 0:
            raise GameServerError('a valid name must be passed to the constructor')

        if self._session == 'auto':
            raise GameServerError('observer mode not available for auto-join sessions')

        response, err, _ = self._send({
            'type':'observe',
            'game':self._game,
            'session':self._session,
            'name':self._name})

        if err: raise GameServerError(err)

        self._player_id = response['player_id']
        self._key = response['key']
        self._observer = True

        return self._player_id

    def restart(self):
        """
        Restart a game.

        This function restarts the current game. There is no need to rejoin the
        session, and all players will keep their IDs. The server ensures that
        all clients will receive the state of the previous game a last time
        before receiving the new game's state. This way they will not miss the
        end/outcome of the previous game.

        Raises:
        GameServerError: in case the game could not be restarted
        """
        if self._observer: raise GameServerError('cannot restart game as observer')

        _, err, _ = self._send({
            'type':'restart',
            'game':self._game,
            'session':self._session,
            'player_id':self._player_id,
            'key':self._key})

        if err: raise GameServerError(err)

    def enable_tls(self, cert=''):
        """
        Calling this function enables TLS encryption. By providing a
        certificate, identity verification of the server is performed in
        addition to encryption.

        The server must have TLS enabled.

        Parameters:
        cert (str): certificate file (optional)

        Raises:
        GameServerError: if loading the certificate failed
        """
        try:
            self._tls_context = ssl.create_default_context()

            if cert:
                cert = self._abs_path(cert)
                self._tls_context.load_verify_locations(cert)
            else:
                self._tls_context.check_hostname = False
                self._tls_context.verify_mode = ssl.CERT_NONE
        except (FileNotFoundError, IsADirectoryError, TypeError):
            raise GameServerError('the specified certificate file could not be found')
        except ssl.SSLError as e:
            raise GameServerError(f'TLS error while loading certificate: {e}')

    def _send(self, data):
        """
        Send data to the server and receive its response.

        This function sends data to the server and returns the data sent back by
        it. The data is sent in JSON format. Make sure, that the passed
        dictionary's content is compatible with JSON.

        Parameters:
        data (dict): data to be sent to the server

        Returns:
        tuple(dict, str, str):
            dict: data returned by server, None in case of an error
            str: error message if a problem occurred, None otherwise
            str: error type in case of an error, okay otherwise
        """
        # prepare data:
        try:
            request = json.dumps(data).encode() + b'EOT\0'
        except:
            return self._api_error('data could not be converted to JSON')

        if len(request) > self._request_size_max:
            return self._api_error('request size limit exceeded')

        # create a socket:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sd:
            with self._secure_socket(sd) as sd:
                try:
                    # connect to server:
                    sd.settimeout(5)
                    sd.connect((self._server, self._port))
                    sd.settimeout(None) # let server handle timeouts
                except ssl.SSLError as e:
                    return self._api_error(f'TLS error: {e}')
                except:
                    return self._api_error(f'unable to connect to {self._server}:{self._port}')

                try:
                    # send data to server:
                    sd.sendall(request)

                    # receive server response:
                    response = bytearray()

                    while True:
                        data = sd.recv(self._buffer_size)
                        if not data: break
                        response += data

                    if not response: raise self._NoResponse
                    response = json.loads(response.decode())

                    # return data:
                    if response['status'] != 'ok': # server responded with an error
                        return None, response['message'], response['status']

                    return response['data'], None, None

                except socket.timeout:
                    return self._api_error('connection timed out')
                except self._NoResponse:
                    return self._api_error('empty or no response received from server')
                except (ConnectionResetError, BrokenPipeError):
                    return self._api_error('connection closed by server')
                except UnicodeDecodeError:
                    return self._api_error('could not decode binary data received from server')
                except json.decoder.JSONDecodeError:
                    return self._api_error('corrupt json received from server')
                except:
                    return self._api_error('unexpected exception:\n' + traceback.format_exc())

    def _secure_socket(self, socket):
        """
        This function wraps the socket and returns a TLS socket. TLS must be
        enabled by calling API function enable_tls. Otherwise, the passed socket
        is returned unmodified. If a certificate was passed to function
        enable_tls, identity verification of the server is enabled. Without a
        certificate, TLS is used for encryption only.

        Parameters:
        socket (socket): a regular socket

        Returns:
        socket or SSLSocket: a TLS socket, if TLS is enabled, the unmodified socket otherwise

        Raises:
        ssl.SSLError: if the creation of the TLS socket failed (lazy, raised after connect())
        """
        if self._tls_context:
            return self._tls_context.wrap_socket(socket, server_hostname=self._server)

        return socket

    def _abs_path(self, file_name):
        """
        Always returns the file name with its absolute path, regardless of where
        the file is located or from where the program was called.

        Parameters:
        file_name (str): file name with relative or absolute path

        Returns:
        str: file name with absolute path

        Raises:
        TypeError: if argument is not of type str
        IsADirectoryError: if argument is a directory
        """
        if not file_name or os.path.isabs(file_name):
            return file_name

        return os.path.join(os.path.abspath(os.path.dirname(__file__)), file_name)

    @staticmethod
    def _api_error(message):
        """
        Return an error message.
        """
        return None, 'api: ' + message, None

    @staticmethod
    def _error(message):
        return 'Invalid argument: ' + message

    class _NoResponse(Exception): pass
