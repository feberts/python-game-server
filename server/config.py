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
ip = '127.0.0.1' # IP, domain or empty string (= all interfaces)
port = 4711

# FRAMEWORK:
game_timeout = 1000 # timeout for inactive game sessions (seconds)

# LOGGING:
log_server_info = True        # general server logging
log_server_errors = True      # errors related to client-server communication
log_server_tcp = False        # useful only for debugging TCP connections
log_framework_info = True     # general framework logging
log_framework_request = True  # client requests such as moves
log_framework_response = True # server responses such as game states

# TCP:
# Pick a higher value for request_size_max if required by a new game.
request_size_max = int(1e6) # size limit for a single request (bytes)

# TLS:
# To enable TLS, specify certificate and key. Clients must enable TLS as well.
tls_cert = '' # certificate in PEM format
tls_key = ''
