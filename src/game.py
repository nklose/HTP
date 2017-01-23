#!/usr/bin/python
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
    user.register()
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
