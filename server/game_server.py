#!/usr/bin/env python3
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
Game server.

This server program opens a port and handles client connections in separate
threads. It passes the data received from a client to the game framework and
sends the framework's reply back to the client. Parameters like IP and port
number are defined in the config file.
"""

import json
import socket
import ssl
import threading
import traceback

import config
import game_framework
import utility

framework = game_framework.GameFramework()

class ClientDisconnect(Exception): pass
class RequestSizeExceeded(Exception): pass

def handle_connection(conn, client):
    """
    Handling a connection.

    This function handles a single connection. It
    - receives data from the client
    - passes that data to the framework
    - sends the data returned by the framework back to the client
    - then closes the connection

    Data is expected to be received in JSON format and it is also sent back to
    the client in JSON format. The connection has a server side timeout and the
    amount of data accepted in a single request is limited by the server. The
    corresponding parameters are defined in the config module. Whenever
    possible, error messages are sent back to the client.

    Parameters:
    conn (socket or SSLSocket): connection socket
    client (tuple(str, int)): client IP and port
    """
    ip, port = client
    log = utility.ServerLogger(ip, port)
    log.info('connection accepted')

    conn.settimeout(config.connection_timeout)

    try:
        try:
            # receive data from client:
            request = bytearray()

            while True:
                data = conn.recv(config.buffer_size)
                if not data: raise ClientDisconnect
                request += data
                if len(request) > config.request_size_max: raise RequestSizeExceeded
                if request.endswith(b'EOT\0'): break

            log.info(f'received {len(request)} bytes: {request}')
            request = request[:-4] # strip EOT
            request = json.loads(request.decode())

            # pass request to the framework:
            try:
                response = framework.handle_request(request)
            except:
                log.error('unexpected exception in the framework:\n' + traceback.format_exc())
                response = utility.framework_error('internal error')

        except RequestSizeExceeded:
            log.error('request size limit exceeded by client')
            response = utility.server_error('request size exceeded by client')
        except socket.timeout:
            log.error('connection timed out on server')
            response = utility.server_error('connection timed out on server')
        except ClientDisconnect:
            log.error('disconnect by client')
            response = None
        except ConnectionResetError:
            log.error('connection reset by client')
            response = None
        except UnicodeDecodeError:
            log.error('could not decode binary data received from client')
            response = utility.server_error('could not decode binary data received from client')
        except json.decoder.JSONDecodeError:
            log.error('corrupt json received from client')
            response = utility.server_error('corrupt json received from client')
        except:
            log.error('unexpected exception on the server:\n' + traceback.format_exc())
            response = utility.server_error('internal error')

        # send response to client:
        if response:
            try:
                response = json.dumps(response).encode()
            except:
                log.error('response could not be converted to JSON')
                response = utility.framework_error('response could not be converted to JSON')
                response = json.dumps(response).encode()

            conn.sendall(response)
            log.info(f'responding: {response}')

    except BrokenPipeError:
        log.error('connection closed by client after sending request')
    except ConnectionResetError:
        log.error('connection reset by client after sending request')
    except:
        log.error('unexpected exception on the server:\n' + traceback.format_exc())
    finally:
        conn.close()
        log.info('connection closed by server')

def secure_socket(socket):
    """
    This function wraps the socket and returns a TLS socket. TLS must be enabled
    in the config module. Otherwise, the passed socket is returned unmodified.
    This function terminates the server program if an error occurs.

    Parameters:
    socket (socket): a regular listening socket

    Returns:
    socket or SSLSocket: a TLS socket, if TLS is enabled, the unmodified socket otherwise
    """
    if config.tls_cert and config.tls_key:
        try:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.load_cert_chain(
                certfile=utility.abs_path(config.tls_cert),
                keyfile=utility.abs_path(config.tls_key))
            print('TLS enabled')

            return context.wrap_socket(socket, server_side=True)

        except (FileNotFoundError, IsADirectoryError, TypeError):
            exit('Error: the specified key or certificate file could not be found')
        except ssl.SSLError as e:
            exit(f'TLS error while loading certificate and key: {e}')

    return socket

print("""This is free software with ABSOLUTELY NO WARRANTY.
Licensed under the GPL version 3 (see LICENSE).
""")

print('Server starting')

# create listening socket:
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sd:
    sd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sd.bind((config.ip, config.port))
    sd.listen()

    with secure_socket(sd) as sd:
        print(f'Listening on {config.ip if config.ip else 'any'}:{config.port}')
        log = utility.ServerLogger()

        # accept connections and handle them in separate threads:
        while True:
            try:
                conn, client = sd.accept()

                threading.Thread(target=handle_connection, args=(conn, client),
                                 daemon=True).start()
            except KeyboardInterrupt:
                print('\nServer shutting down')
                exit()
            except ssl.SSLError as e:
                log.error(f'TLS error: {e}')
            except:
                log.error('unexpected exception on the server:\n' + traceback.format_exc())
