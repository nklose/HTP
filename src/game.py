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

# File: game.py
# This is the main entry point for the game.

import pwd
import time
import signal
import subprocess

import GameController as gc
import CommandController as cc

from User import User
from File import File
from Computer import Computer
from Directory import Directory
from MessageBox import MessageBox
from ChatSession import ChatSession

from threading import Thread
from datetime import datetime
from termcolor import colored

# Handle keyboard interrupt shortcuts
def signal_handler(signum, frame):
    pass # prevent exiting
#signal.signal(signal.SIGTSTP, signal_handler)  # Disable Ctrl-Z
#signal.signal(signal.SIGINT, signal_handler)   # Disable Ctrl-C

def main():
    gc.clear()

    gc.typewriter(colored('\n\tWelcome to Hack the Planet!', 'green', attrs = ['bold']))

    valid_choice = False
    while not valid_choice:
        gc.msg('\n  1. Log In')
        gc.msg('2. Register')
        gc.msg('3. Reset Password')
        gc.msg('4. About Hack the Planet')

        choice = cc.prompt_num()

        # log in
        if choice == '1':
            login()
        # register
        elif choice == '2':
            register()
        # reset password
        elif choice == '3':
            u = User()
            u.reset_password()
        # about
        elif choice == '4':
            about()
        # invalid
        else:
            gc.error('Invalid choice; please try again.')

## Navigation
# Shows a user's profile summary
def profile(user, new_login = False):
    user.show_summary()
    user.computer.show_login_banner()
    gc.info('Enter \'help\' for a list of commands.\n')
    if new_login: # update last login timestamp if user just logged in
        user.new_login()
    cc.prompt(user)

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
    profile(user, new_login = True)

# Register a new user account
def register():
    user = User()
    user.register()
    profile(user, new_login = True)

if __name__ == '__main__':
    main()
