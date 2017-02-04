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
import sys
import time
import hashlib
import random

from getpass import getpass
from datetime import datetime, timedelta
from termcolor import colored

from User import User
from Database import Database

# constants
DEBUG_LEVEL = 1                      # verbosity; 0=disabled, 1=important, 2=info
GAME_VERSION = 0.1                   # current version of HTP
GAME_TIMESTAMP = '2016-01-23'        # date on which game was last updated
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'    # standard timestamp format
CMD_LOG_DIR = '../cmd_log'           # directory to store logs of user commands
NOTE_DIR = '../data/notes'           # directory to store in-game notes
NPC_DIR = '../data/npcs'             # directory to store NPC info files
PROGRAM_DIR = '../data/programs'     # data to store binary descriptions
CMD_LOG_LENGTH = 100                 # number of commands per user to save
MAX_FILE_SIZE = 4096                 # max characters allowed in a file
DIR_MAX_LENGTH = 16                  # max chars for a directory name
DIR_MAX_NEST = 6                     # directory nesting maximum
DIR_SIZE = 32                        # size on disk one directory takes up
FILE_MAX_LENGTH = 32                 # max length of a file name
BOX_WIDTH = 80                       # width of text box in characters
LONG_FILE_CUTOFF = 10000             # length at which a file is considered a long file
CONTACT_EMAIL = 'spartandominion@gmail.com'

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

# Generate a random unique token
def gen_token():
    token = ''
    unique = False
    db = Database()
    while not unique:
        token = ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for i in range(12))
        sql = 'SELECT * FROM users WHERE token = %s'
        args = [token]
        response = db.get_query(sql, args)
        if len(response) == 0:
            unique = True
    db.close()
    return token

# Generate a random IP
def gen_ip():
    new_ip = ''
    db = Database()
    valid_ip = False
    while not valid_ip:
        w, x, y, z = 0, 0, 0, 0
        while x == 0 and w in (0, 10, 127, 192):
            w = random.randint(1, 255)
            x = random.randint(0, 255)
            y = random.randint(0, 255)
            z = random.randint(0, 255)
        new_ip = str(w) + '.' + str(x) + '.' + str(y) + '.' + str(z)

        sql = 'SELECT * FROM computers WHERE ip = %s'
        args = [new_ip]
        response = db.get_query(sql, args)
        if len(response) == 0:
            valid_ip = True
    db.close()
    return new_ip

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

# Typewriter-like animation
def typewriter(message):
    for c in message:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(random.uniform(0, 0.2))
    sys.stdout.write('\n')

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
    elif str == 'bin':
        return 'Executable Program'

# converts other units (KB, MB, GB) to bytes
def to_bytes(amt, units):
    if units.lower() == 'kb':
        return amt * 1024
    elif units.lower() == 'mb':
        return amt * 1024 * 1024
    elif units.lower() == 'gb':
        return amt * 1024 * 1024 * 1024
    else:
        error('An error occurred during a unit conversion.')

# prints a horizontal line to the screen
def hr():
    i = 0
    line = ''
    while i < BOX_WIDTH:
        line += u'\u2500'
        i += 1
    print line

# attempts a password reset on an account
def reset_password():
    db = Database()
    msg('Beginning the password reset process...')
    username = raw_input('  Please enter your username: ')
    user = User()
    user.name = username
    user.lookup()
    # check if the user is registered
    if user.exists:
        # check if they already have a reset token
        if user.email == '':
            error('Sorry, you are not eligible to use the password reset feature.')
            warning('Only accounts with a valid email address attached can use this feature.')
            msg('Please contact our staff at ' + CONTACT_EMAIL + ' for further assistance.')
        elif user.token == '':
            # generate a token and send it to the user
            user.confirm_email()
            user.save()
            msg('Please check your email for a validation code, then use the \'Reset Password\' feature again.')
        elif user.token_date < string_to_ts(current_time()) - timedelta(days = 1):
            warning('Your reset token has expired. Sending another one...')
            user.confirm_email()
            user.save()
        else:
            token = raw_input('  Please enter your reset token: ')
            if token == user.token:
                msg('You can now set a password for your account.')
                valid_password = False
                while not valid_password:
                    password = getpass()
                    if len(password) < 6:
                        error('Your password must contain 6 or more characters.')
                    else:
                        confirm = getpass('Confirm: ')
                        if password != confirm:
                            error('Sorry, those passwords didn\'t match.')
                        else:
                            valid_password = True
                            user.password = hash_password(password, user.name)
                user.token = ''
                user.save()
            else:
                warning('Sorry, that token is not valid. Sending another one...')
                user.confirm_email()
                user.save()

    else:
        error('Sorry, that username is not registered.')
    db.close()