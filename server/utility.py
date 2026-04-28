"""
Utility.

This module provides various utility functions and classes.
"""

from datetime import datetime
import os

import config

def _generic_error(sender, message, status='error'):
    """
    Create an error message.

    The message is embedded into a dictionary, which is sent back to the client.
    To let the client know where the error was detected, the sender is prepended
    to the message. The sender is omitted, if the message parameter is of a type
    other than string (see function AbstractGame.move).

    Parameters:
    sender (str): let client know where the error was detected
    message: error message (see above for details)
    status (str): error status

    Returns:
    dict: contains the message
    """
    if type(message) == str:
        message = sender + ': ' + message

    return {'status':status, 'message':message}

def server_error(message):
    """
    Server error. See function _generic_error for details.
    """
    return _generic_error('server', message)

def framework_error(message):
    """
    Framework error. See function _generic_error for details.
    """
    return _generic_error('framework', message)

def game_error(message):
    """
    Game error. See function _generic_error for details.
    """
    return _generic_error('game', message, 'illegalmove')

class ServerLogger:
    """
    Logging server information.

    The output contains a timestamp, the client's IP and port, and the log
    message itself. The log level can be set in the config file.
    """
    def __init__(self, ip=None, port=None):
        """
        Parameters:
        ip (str): client IP
        port (int): client port
        """
        self._client = f' {ip}:{port}' if ip else ''

    def tcp(self, message):
        """
        Log TCP related information. See function _log for details.
        """
        if config.log_server_tcp:
            self._log(message)

    def error(self, message):
        """
        Log server errors. See function _log for details.
        """
        if config.log_server_errors:
            self._log(message)

    def _log(self, message):
        """
        Print log message.

        Parameters:
        message (str): message
        """
        time = datetime.strftime(datetime.now(), '%Y-%m-%d %X')
        print(f'[{time}{self._client}] {message}')

class FrameworkLogger:
    """
    Logging framework information.

    The log level can be set in the config file.
    """
    def info(self, message):
        """
        Logging actions initiated by the framework.

        Parameters:
        message (str): message
        """
        if config.log_framework_actions:
            self._log(message)

    def request(self, request):
        """
        Logging client requests.

        Parameters:
        request (dict): client request
        """
        if config.log_framework_request:
            self._log(f'Request:  {request}')

    def response(self, response):
        """
        Logging server responses.

        Parameters:
        response (dict): server response
        """
        if config.log_framework_response:
            self._log(f'Response: {response}')

    def _log(self, message):
        print(message)

def check_dict(d, expected):
    """
    Checking a dictionary's structure.

    This function verifies, that all expected keys are present in a given
    dictionary and that their values are of the expected types.

    Example: To check if dictionary d has a key named 'a' that maps to a value
    of type int or float and a key named 'b' that maps to a value of type str,
    a function call might look like this:

    d = {'a':42, 'b':'forty-two'}
    err = check_dict(d, {'a':(int, float), 'b':str})
    if err: print(err)

    Parameters:
    d (dict): dictionary to be checked
    expected (dict): contains the expected key names and value data types

    Returns:
    str: None, if dictionary has the expected structure, an error message otherwise
    """
    for key_name, val_type in expected.items():
        if key_name not in d:
            return f"key '{key_name}' of type {val_type} missing"
        if not isinstance(d[key_name], val_type):
            return f"value of key '{key_name}' must be of type {val_type}"

    return None

def abs_path(file_name):
    """
    Always returns the file name with its absolute path, regardless of where the
    file is located or from where the program was called.

    Parameters:
    file_name (str): file name with relative or absolute path

    Returns:
    str: file name with absolute path

    Raises:
    TypeError: if argument is not of type str
    IsADirectoryError: if argument is a directory
    """
    if os.path.isabs(file_name):
        return file_name

    return os.path.join(os.path.abspath(os.path.dirname(__file__)), file_name)
