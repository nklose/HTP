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
import string
import random
import hashlib

from getpass import getpass
from datetime import datetime, timedelta
from termcolor import colored

from Database import Database
from MessageBox import MessageBox

# constants
DEBUG_LEVEL = 1                      # verbosity; 0=disabled, 1=important, 2=info
GAME_VERSION = 0.1                   # current version of HTP
GAME_TIMESTAMP = '2016-01-23'        # date on which game was last updated
OS_MEMORY = 52                       # base memory in MB used by the OS
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'    # standard timestamp format
CMD_LOG_DIR = '../cmd_log'           # directory to store logs of user commands
NOTE_DIR = '../data/notes'           # directory to store in-game notes
NPC_DIR = '../data/npcs'             # directory to store NPC info files
PROGRAM_DIR = '../data/programs'     # directory to store binary descriptions
BANNER_DIR = '../data/banners'       # directory to store NPC banner text files
CMD_LOG_LENGTH = 100                 # number of commands per user to save
MAX_FILE_SIZE = 4096                 # max characters allowed in a file
DIR_MAX_LENGTH = 16                  # max chars for a directory name
DIR_MAX_NEST = 6                     # directory nesting maximum
DIR_MAX_COUNT = 16                   # maximum number of directories per computer
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
    return gen_string(random.randint(8, 12))

# Generate a random unique token
def gen_token():
    token = ''
    unique = False
    db = Database()
    while not unique:
        token = gen_string(12)
        sql = 'SELECT * FROM users WHERE token = %s'
        args = [token]
        response = db.get_query(sql, args)
        if len(response) == 0:
            unique = True
    db.close()
    return token

# Generates a random name for an activated virus
def gen_virus_name():
    return gen_string(8) + '.bin'

# Generates a randomized string of specified length
def gen_string(length):
    return ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for i in range(length))

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

# Prompts the user for text input
def prompt(message):
    return raw_input(colored('  ' + message + ': ', 'cyan')).lower()

# Prompts the user with a yes or no question
def prompt_yn(message, default = 'y'):
    yn_str = ''
    if default == 'y':
        yn_str = ' (Y/n): '
    else:
        yn_str = ' (y/N): '
    choice = raw_input(colored('  ' + message + yn_str, 'cyan')).lower()
    return choice == 'y' or (choice == '' and default == 'y')

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
        time.sleep(random.uniform(0.000, 0.050))
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

# Returns a human-readable string from a number of seconds
def hr_seconds(num):
    dt = datetime(1, 1, 1) + timedelta(seconds = num)
    return '%d:%d:%d' % (dt.hour, dt.minute, dt.second)

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

# shows the help text
def show_help():
    mb = MessageBox()
    mb.set_title('Command List')
    mb.set_label_width(25)
    mb.add_heading('Basic Commands')
    mb.add_property('chat', 'opens the global chat room')
    mb.add_property('disk', 'shows information about disk usage')
    mb.add_property('log', 'prints out the system log')
    mb.add_property('summary', 'shows the login summary again')
    mb.add_heading('Files and Directories')
    mb.add_property('ls (dir)', 'lists objects in the current directory')
    mb.add_property('cd <dir>', 'jumps to the directory <dir>')
    mb.add_property('edit <file>', 'starts text editor for <file>')
    mb.add_property('view (cat) <file>', 'outputs the contents of <file>')
    mb.add_property('md (mkdir) <name>', 'creates a new directory called <name>')
    mb.add_property('mf (mkfile) <name>', 'creates a new test file called <name>')
    mb.add_property('rm (del) <obj>', 'permanently deletes <obj> and its contents')
    mb.add_property('cp (copy) <obj> <dest>', 'creates a copy of <obj> named <dest>')
    mb.add_property('rn (rename) <obj> <name>', 'sets <obj>\'s name to <name>')
    mb.add_property('mv (move) <obj> <dir>', 'moves <obj> to directory <dir>')
    mb.add_property('info <obj>', 'shows detailed info about <obj>')
    mb.add_property('processes (ps)', 'shows running processes with ID numbers')
    mb.add_property('close (stop) <id>', 'finishes a running process')
    mb.add_heading('Networking')
    mb.add_property('ping <target>', 'sends an echo request to the IP or domain <target>')
    mb.add_property('ssh <target>', 'attempts to log into IP or domain <target>')
    mb.add_property('ul (upload) <path>', 'uploads the object at local path <path>')
    mb.add_property('dl (download) <obj>', 'downloads the object <obj> to ~/downloads')
    mb.add_property('chip', 'changes your ip (can only be done once per day)')
    mb.display()

# checks if a given filename matches naming requirements
def valid_filename(filename):
    allowed_chars = string.ascii_lowercase + string.digits + '.-_'
    return all(c in allowed_chars for c in filename)

# checks if a given directory name matches naming requirements
def valid_dirname(dirname):
    allowed_chars = string.ascii_lowercase + string.digits + '-_'
    return all(c in allowed_chars for c in dirname)