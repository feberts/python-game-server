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
ip = '127.0.0.1'
port = 4711

# FRAMEWORK:
game_timeout = 1000 # seconds, timeout for inactive games and for joining a game

# LOGGING:
log_server_info = False # useful for debugging tcp connections (verbose)
log_server_errors = True # errors during tcp connections
log_framework_request = True # client requests
log_framework_response = True # server responses
log_framework_actions = True # actions performed by the framework, such as terminating games

# TCP CONNECTIONS:
# pick a higher value for request_size_max if required by a new game;
# it should not be necessary to change buffer_size or connection_timeout
request_size_max = int(1e6) # bytes, prevents clients from sending too much data
buffer_size = 4096 # bytes, corresponds to client-side buffer size value
connection_timeout = 60 # seconds, timeout for tcp transactions
