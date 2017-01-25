# Main controller for HTP
# Collection of universal utility functions
import os
import time
import hashlib
import random

from datetime import datetime
from termcolor import colored

# constants
GAME_VERSION = 0.1                  # current version of HTP
GAME_TIMESTAMP = '2016-01-23'       # date on which game was last updated
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'   # standard timestamp format
DIR_MAX_LENGTH = 16                 # max chars for a directory name
DIR_MAX_NEST = 6                    # directory nesting maximum
DIR_SIZE = 32                       # size on disk one directory takes up
FILE_MAX_LENGTH = 32                # max length of a file name
DEBUG_LEVEL = 2                     # verbosity; 0=disabled, 1=important, 2=info
BOX_WIDTH = 70                      # width of text box in characters
LONG_FILE_CUTOFF = 10000            # length at which a file is considered a long file

# gets the current timestamp
def current_time():
    ts = time.time()
    return datetime.fromtimestamp(ts).strftime(TIME_FORMAT)

# converts a string to a timestamp
def string_to_ts(string):
    return datetime.strptime(string, TIME_FORMAT)

# converts a timestamp to a string
def ts_to_string(ts):
    return datetime.strftime(ts, TIME_FORMAT)

# Generate a random password
def gen_password():
    length = random.randint(8, 12)
    return ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for i in range(length))

# Generate a random IP
def gen_ip():
    w, x, y, z = 0, 0, 0, 0
    while x == 0 and w in (0, 10, 127, 192):
        w = random.randint(1, 255)
        x = random.randint(0, 255)
        y = random.randint(0, 255)
        z = random.randint(0, 255)
    return str(w) + '.' + str(x) + '.' + str(y) + '.' + str(z)

## Password Hashing
# Create a hash string from a password and username
def hash_password(password, salt):
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

# Check a hashed password
def check_hash(password, hashed_pw):
    hashed_pw, salt = hashed_pw.split(':')
    return hashed_pw == hashlib.sha256(salt.encode() + password.encode()).hexdigest()

## Output Messages
# Standard Message
def msg(message):
    print(colored('  ' + message, 'cyan'))

# Success Message
def success(message):
    print(colored('  ' + message, 'green'))

# Warning Message
def warning(message):
    print(colored('  ' +message, 'yellow'))

# Error Message
def error(message):
    print(colored('  ' + message, 'red'))

# Report Bug Message
def report(id):
    print(colored('  [E' + str(id) + ']: An unexpected error occurred. Please report this bug.'))

# Info Message
def info(message):
    print(colored('  ' + message, 'blue'))

# Paired Message
def msg_pair(msg1, msg2):
    print(colored('  ' + msg1 + ' ', 'cyan') + colored(msg2, 'white'))

# Debug Message
def debug(message, level = 2):
    if DEBUG_LEVEL >= level:
        label = ''
        if level == 1:
            label = colored('  [DEBUG] ', 'red')
        elif level == 2:
            label = colored('  [INFO] ', 'yellow')
        print(label + colored(message, 'white'))

# Clear screen
def clear():
    os.system('clear')

# Returns a number of bytes as a human-readable string
def hr_bytes(num):
    # gigabytes
    if num > 1024 * 1024 * 1024 * 5:
        return str(num / 1024 / 1024 / 1024) + ' GB'
    elif num > 1024 * 1024 * 5:
        return str(num / 1024 / 1024) + ' MB'
    elif num > 1024 * 5:
        return str(num / 1024) + ' KB'
    else:
        return str(num) + ' B'

# Returns detailed file type from extension string
def str_to_type(str):
    if str == 'txt':
        return 'Plain Text'
    elif str == 'exe':
        return 'Executable Program'
