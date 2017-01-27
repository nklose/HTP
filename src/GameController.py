#################################################
#   __   ____  ____  _________  _______   __    #
# .' _| |_   ||   _||  _   _  ||_   __ \ |_ `.  #
# | |     | |__| |  |_/ | | \_|  | |__) |  | |  #
# | |     |  __  |      | |      |  ___/   | |  #
# | |_   _| |  | |_    _| |_    _| |_     _| |  #
# `.__| |____||____|  |_____|  |_____|   |__,'  #
#                                               #
#   48 61 63 6B  54 68 65  50 6C 61 6E 65 74    #
#################################################

# File: GameController.py
# Collection of general utility functions for the game.

import os
import time
import hashlib
import random

from datetime import datetime
from termcolor import colored

# constants
GAME_VERSION = 0.1                   # current version of HTP
GAME_TIMESTAMP = '2016-01-23'        # date on which game was last updated
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'    # standard timestamp format
CMD_LOG_DIR = '../cmd_log'           # directory to store logs of user commands
CMD_LOG_LENGTH = 100                 # number of commands per user to save
DIR_MAX_LENGTH = 16                  # max chars for a directory name
DIR_MAX_NEST = 6                     # directory nesting maximum
DIR_SIZE = 32                        # size on disk one directory takes up
FILE_MAX_LENGTH = 32                 # max length of a file name
DEBUG_LEVEL = 2                      # verbosity; 0=disabled, 1=important, 2=info
BOX_WIDTH = 70                       # width of text box in characters
LONG_FILE_CUTOFF = 10000             # length at which a file is considered a long file

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

# Prompts the user with a yes or no question
def prompt_yn(message):
    return raw_input(colored('  ' + message + ' (Y/N): ', 'cyan')).lower() == 'y'

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
    num_bytes = float(num)
    num_kb = num_bytes / 1024.0
    num_mb = num_kb / 1024.0
    num_gb = num_mb / 1024.0
    if num_gb > 1:
        return str(round(num_gb, 2)) + ' GB'
    elif num_mb > 1:
        return str(round(num_mb, 2)) + ' MB'
    elif num_kb > 1:
        return str(round(num_kb, 2)) + ' KB'
    else:
        return hr_large(int(num_bytes)) + ' B'

# Adds separation commas to a large number and returns it as a string
def hr_large(num):
    return '{:,}'.format(num)

# Returns detailed file type from extension string
def str_to_type(str):
    if str == 'txt':
        return 'Plain Text'
    elif str == 'exe':
        return 'Executable Program'

