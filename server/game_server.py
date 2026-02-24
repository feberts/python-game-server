#!/usr/bin/env python3
"""
Game server.

A lightweight server and framework for turn-based multiplayer games.
Copyright (C) 2025, 2026 Fabian Eberts
Licensed under the GPL v3.0 (see LICENSE)

This server program opens a port and handles client connections in separate
threads. It passes the data received from a client to the game framework and
sends the framework's reply back to the client. Parameters like IP or port
number are defined in the config file.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

import json
import socket
import threading
import traceback

import config
import game_framework
import utility

framework = game_framework.GameFramework()

class ClientDisconnect(Exception): pass
class RequestSizeExceeded(Exception): pass

def handle_connection(conn, ip, port):
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
    conn (socket): connection socket
    ip (str): client IP
    port (int): client port
    """
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

# start the server:
print('This is free software with ABSOLUTELY NO WARRANTY.')
try:
    # create listening socket:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sd:
        sd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sd.bind((config.ip, config.port))
        sd.listen()

        print(f'Listening on {config.ip}:{config.port}')

        while True:
            # accept a connection:
            conn, client = sd.accept()
            ip, port = client

            # handle connection in separate thread:
            t = threading.Thread(target=handle_connection, args=(conn, ip, port), daemon=True)
            t.start()
except KeyboardInterrupt:
    print('')
