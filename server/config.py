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
Server and framework configuration.
"""

# SERVER:
ip = '127.0.0.1' # IP, domain name or empty string (= all interfaces)
port = 4711

# FRAMEWORK:
game_timeout = 1000 # seconds, timeout for inactive games and for joining a game

# LOGGING:
log_server_errors = True      # errors related to client-server communication
log_server_tcp = False        # useful for debugging TCP connections
log_framework_request = True  # client requests such as moves, game state or join request
log_framework_response = True # server responses such as game states or error messages
log_framework_actions = True  # starting and terminating game sessions

# TCP:
# Pick a higher value for request_size_max if required by a new game.
request_size_max = int(1e6) # bytes, prevents clients from sending too much data

# TLS:
# To enable TLS, specify certificate and key. Clients must enable TLS as well.
# Enabled TLS is indicated by a log message on server startup.
tls_cert = '' # certificate in PEM format
tls_key = ''
