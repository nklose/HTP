#!/usr/bin/python
import re
import signal
import subprocess
import pwd
import time
import GameController as gc

from MessageBox import MessageBox
from User import User
from Computer import Computer
from Database import Database
from ChatSession import ChatSession
from File import File
from Directory import Directory

from datetime import datetime
from threading import Thread

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
        gc.msg('\n  1. Log In')
        gc.msg('2. Register')
        gc.msg('3. Reset Password')
        gc.msg('4. About Hack the Planet')

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
            gc.error('Invalid choice; please try again.')

## Navigation
# Shows a user's profile summary
def profile(user):
    user.show_summary()
    gc.info('Enter \'help\' for a list of commands.\n')
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
    user = User()
    user.login()
    profile(user)

# Register a new user account
def register():
    user = User()
    gc.msg('\nStarting the account creation process...')
    gc.msg('Your username can be between 4 and 16 characters and must be alphanumeric.')
    valid_user = False
    db = Database()
    while not valid_user:
        user.name = raw_input('Desired Username: ')

        # name cannot be blank
        if user.name == '':
            gc.error('You must enter a username.')
        # name must be alphanumeric; symbols are rejected prior to database lookup
        elif not user.name.isalnum():
            gc.error('Your username can only contain letters and numbers.')
        # name must be between 4 and 16 characters
        elif len(user.name) < 4 or len(user.name) > 16:
            gc.error('Your username must be between 4 and 16 characters.')
        # name must not already exist in database
        else:
            sql = 'SELECT * FROM users WHERE username = %s;'
            response = db.get_query(sql, [user.name])
            if len(response) > 0:
                gc.error('Sorry, that name is taken. Please choose another.')
            else:
                gc.msg('Username is available!')
                valid_user = True

    # get a valid password
    gc.msg('\n  You can now set a password for your account.')
    valid_password = False
    while not valid_password:
        password = getpass()
        confirm = getpass('Confirm: ')
        if len(password) < 6:
            gc.error('Your password must contain 6 or more characters.')
        elif password != confirm:
            gc.error('Sorry, those passwords didn\'t match.')
        else:
            valid_password = True
            user.password = gc.hash_password(password, user.name)

    # get a valid email address
    valid_email = False
    gc.msg('\n  You will need to enter a valid email in case you forget your password.')
    while not valid_email:
        user.email = raw_input('Email Address: ')
        if re.match(r'[^@]+@[^@]+\.[^@]+', user.email):
            # check if email exists in database
            sql = 'SELECT * FROM users WHERE email = %s;'
            response = db.get_query(sql, [user.email])
            if len(response) > 0:
                gc.error('Sorry, that email has already been registered.')
            else:
                valid_email = True
        else:
            gc.error('Sorry, your input was not in the right format for an email address.')

    # get a unique in-game handle
    gc.msg('\n  Finally, you need to choose an in-game handle that others can see.')
    gc.msg('This is separate from your username, and can be changed later.')
    valid_handle = False
    while not valid_handle:
        user.handle = raw_input('Please enter a handle: ')
        if user.handle == '':
            gc.error('You must enter a handle.')
        elif not user.handle.isalnum():
            gc.error('Your handle can only contain letters and numbers.')
        elif len(user.handle) < 2 or len(user.handle) > 16:
            gc.error('Your handle must be between 2 and 16 characters.')
        else:
            sql = 'SELECT * FROM users WHERE handle = %s;'
            response = db.get_query(sql, [user.handle])
            if len(response) > 0:
                gc.error('Sorry, that handle is taken. Please choose another.')
            else:
                valid_handle = True

    # generate an IP address for the user
    valid_ip = False
    while not valid_ip:
        user.computer.ip = gc.gen_ip()
        # check if the IP has been assigned already
        sql = 'SELECT * FROM computers WHERE ip = %s;'
        response = db.get_query(sql, [user.computer.ip])
        if len(response) == 0:
            valid_ip = True

    user.save()     # write user to database
    user.lookup()   # get generated id for the user

    # update computer information
    user.computer.password = gc.gen_password()
    user.computer.owner_id = user.id

    user.computer.save()     # write computer to database
    user.computer.lookup()   # get generated id for computer

    user.save()

    gc.success('\n Account ' + user.name + ' created!')

    # close database
    db.close()
    profile(user)

# Establish a connection to IRC
def show_chat(user):
    print('Connecting to chat server...')
    cs = ChatSession(user.handle)
    profile(user)

# Prompt the user for input and respond accordingly.
def prompt(user):
    db = Database()
    directory = Directory(user.name)
    show_prompt = True
    while show_prompt:
        command = raw_input(user.name + ':' + directory.name + '$ ').lower()
        if command == 'help':
            gc.msg('Command list:')
            gc.msg('- chat - opens chat room')
            gc.msg('- ls/dir - shows objects in current directory')
            gc.msg('- cd - changes directory; use .. to go up one level')
            gc.msg('- edit [file] - starts editing a text file')
        elif command == 'chat':
            show_chat(user)
        elif command == 'newfile':
            pass
        elif command in ['ls', 'dir']:
            directory.print_contents()
        elif command == 'exit':
            show_prompt = False
            # exit script and disconnect from server
            exit()
        else:
            gc.error('Sorry, your input was not understood.')

    # close database
    db.close()

# Prompt for a numeric input
def prompt_num():
    return raw_input('\n# ')

if __name__ == '__main__':
    main()
