#!/usr/bin/python
import re
import signal
import subprocess
import random
import pwd
import time
import hashlib
import curses

from MessageBox import MessageBox
from User import User
from Computer import Computer
from Database import Database
from ChatSession import ChatSession
from File import File
from Directory import Directory

from datetime import datetime
from threading import Thread
from getpass import getpass
from termcolor import colored

# Handle keyboard interrupt shortcuts
def signal_handler(signum, frame):
    pass # prevent exiting
#signal.signal(signal.SIGTSTP, signal_handler)  # Disable Ctrl-Z
#signal.signal(signal.SIGINT, signal_handler)   # Disable Ctrl-C

def main():
    print('\n')

    print('\tWelcome to Hack the Planet!')

    valid_choice = False
    while not valid_choice:
        msg('\n  1. Log In')
        msg('2. Register')
        msg('3. Reset Password')
        msg('4. About Hack the Planet')

        choice = prompt_num()

        # log in
        if choice == '1':
            login()
        # register
        elif choice == '2':
            register()
        # reset password
        elif choice == '3':
            pass
        # about
        elif choice == '4':
            about()
        # invalid
        else:
            error('Invalid choice; please try again.')

## Navigation
# Shows a user's profile summary
def profile(user):
    show_user_summary(user)
    info('Enter \'help\' for a list of commands.\n')
    prompt(user)

# Shows info about the game
def about():
    # read about file
    file = open('../data/about.txt', 'r')
    long_text = file.readlines()
    file.close()

    # print in a message box
    msg_box = MessageBox()
    msg_box.set_title('About Hack the Planet')
    for line in long_text:
        msg_box.add_long_text(line)
        msg_box.blank_line()
    msg_box.display()

## Main Menu Options
# Log in an existing account
def login():
   # check user credentials
    db = Database()
    valid_creds = False
    attempts = 1
    while not valid_creds:
        username = raw_input('Username: ')
        password = getpass()

        sql = 'SELECT password FROM users WHERE username = %s'
        password_hash = db.get_query(sql, [username])

        if attempts > 4:
            error('Disconnecting after 5 failed login attempts.')
            exit()
        elif len(password_hash) == 0 or not check_hash(password, password_hash[0][0]):
            time.sleep(2)
            error('Invalid credentials. Please try again.')
            attempts += 1
        else:

            success('Credentials validated. Logging in...')
            user = User(username)
            user.lookup()
            profile(user)

    # close database
    db.close()

# Register a new user account
def register():
    user = User()
    computer = Computer()
    msg('\nStarting the account creation process...')
    msg('Your username can be between 4 and 16 characters and must be alphanumeric.')
    valid_user = False
    db = Database()
    while not valid_user:
        user.name = raw_input('Desired Username: ')

        # name cannot be blank
        if user.name == '':
            error('You must enter a username.')
        # name must be alphanumeric; symbols are rejected prior to database lookup
        elif not user.name.isalnum():
            error('Your username can only contain letters and numbers.')
        # name must be between 4 and 16 characters
        elif len(user.name) < 4 or len(user.name) > 16:
            error('Your username must be between 4 and 16 characters.')
        # name must not already exist in database
        else:
            sql = 'SELECT * FROM users WHERE username = %s;'
            response = db.get_query(sql, [user.name])
            if len(response) > 0:
                error('Sorry, that name is taken. Please choose another.')
            else:
                msg('Username is available!')
                valid_user = True

    # get a valid password
    msg('\n  You can now set a password for your account.')
    valid_password = False
    while not valid_password:
        password = getpass()
        confirm = getpass('Confirm: ')
        if len(password) < 6:
            error('Your password must contain 6 or more characters.')
        elif password != confirm:
            error('Sorry, those passwords didn\'t match.')
        else:
            valid_password = True
            user.password = hash_password(password, user.name)

    # get a valid email address
    valid_email = False
    msg('\n  You will need to enter a valid email in case you forget your password.')
    while not valid_email:
        user.email = raw_input('Email Address: ')
        if re.match(r'[^@]+@[^@]+\.[^@]+', user.email):
            # check if email exists in database
            sql = 'SELECT * FROM users WHERE email = %s;'
            response = db.get_query(sql, [user.email])
            if len(response) > 0:
                error('Sorry, that email has already been registered.')
            else:
                valid_email = True
        else:
            error('Sorry, your input was not in the right format for an email address.')

    # get a unique in-game handle
    msg('\n  Finally, you need to choose an in-game handle that others can see.')
    msg('This is separate from your username, and can be changed later.')
    valid_handle = False
    while not valid_handle:
        user.handle = raw_input('Please enter a handle: ')
        if user.handle == '':
            error('You must enter a handle.')
        elif not user.handle.isalnum():
            error('Your handle can only contain letters and numbers.')
        elif len(user.handle) < 2 or len(user.handle) > 16:
            error('Your handle must be between 2 and 16 characters.')
        else:
            sql = 'SELECT * FROM users WHERE handle = %s;'
            response = db.get_query(sql, [user.handle])
            if len(response) > 0:
                error('Sorry, that handle is taken. Please choose another.')
            else:
                valid_handle = True

    # generate an IP address for the user
    valid_ip = False
    while not valid_ip:
        computer.ip = gen_ip()
        # check if the IP has been assigned already
        sql = 'SELECT * FROM computers WHERE ip = %s;'
        response = db.get_query(sql, [computer.ip])
        if len(response) == 0:
            valid_ip = True

    user.save()     # write user to database
    user.lookup()   # get generated id for the user

    # update computer information
    computer.password = gen_password()
    computer.owner_id = user.id

    computer.save()     # write computer to database
    computer.lookup()   # get generated id for computer

    user.computer_id = computer.id
    user.save()

    success('\n Account ' + user.name + ' created!')

    # close database
    db.close()
    profile(user)

# Establish a connection to IRC
def show_chat(username, handle):
    print('Connecting to chat server...')
    cs = ChatSession(handle)
    profile(username)

## Common operations
def show_user_summary(user):
    # initialize database
    db = Database ()

    # get bank account info
    sql = 'SELECT funds FROM bank_accounts WHERE owner_id = %s'
    response = db.get_query(sql, [user.id])
    num_accounts = 0
    total_funds = 0
    if response is not None:
        num_accounts = len(response)
        i = 0
        while i < len(response):
            total_funds += int(response[i][0])
            i += 1

    # close database
    db.close()

    # display all info
    c = user.computer
    msg_box = MessageBox()
    msg_box.set_title('User Summary')
    msg_box.add_property('RAM', str(c.ram) + ' MB')
    msg_box.add_property('CPU', str(c.cpu) + ' MHz')
    msg_box.add_property('Disk', str(c.hdd) + ' GB')
    msg_box.add_property('Free', str(c.disk_free) + ' GB')
    msg_box.add_property('Firewall', 'Level ' + str(c.fw_level))
    msg_box.add_property('Antivirus', 'Level ' + str(c.av_level))
    msg_box.add_property('Cracker', 'Level ' + str(c.cr_level))
    msg_box.hr()
    msg_box.add_property('IP Address', c.ip)
    msg_box.add_property('Comp. Password', str(c.password))
    msg_box.hr()
    # add user details
    msg_box.add_property('Handle', user.handle)
    msg_box.add_property('Last Login', str(user.last_login))
    # number of bank accounts
    msg_box.add_property('Total Funds', str(total_funds) + ' dollars')
    msg_box.add_property('# of Accounts', str(num_accounts))

    msg_box.display()

# Prompt the user for input and respond accordingly.
def prompt(user):
    db = Database()
    directory = Directory(user.name)
    show_prompt = True
    while show_prompt:
        command = raw_input(user.name + ':' + directory.name + '$ ').lower()
        if command == 'help':
            msg('Help text will go here.')
        elif command == 'chat':
            show_chat(user)
        elif command == 'newfile':
            pass
        elif command in ['ls', 'dir']:
            msg('Showing concents of ' + directory.name + ':')
            msg(directory.get_contents())
        elif command == 'exit':
            show_prompt = False
            # exit script and disconnect from server
            exit()
        else:
            error('Sorry, your input was not understood.')

    # close database
    db.close()

# Prompt for a numeric input
def prompt_num():
    return raw_input('\n# ')

# Prompt for chat input
def prompt_chat(username):
    return raw_input('[' + username + '] ')

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

# Info Message
def info(message):
    print(colored('  ' + message, 'blue'))

# Get current time as string
def get_timestamp():
    ts = time.time()
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

# Converts a string to a timestamp
def read_timestamp(str):
    if len(str) > 0:
        return datetime.strptime(str, '%Y-%m-%d %H:%M:%S')
    else:
        warning('Blank line encountered in ' + logfile)


if __name__ == '__main__':
    main()
