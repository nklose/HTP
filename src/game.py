#!/usr/bin/python
import os
import pwd
import time
import signal
import atexit
import readline
import subprocess

import GameController as gc

from User import User
from File import File
from Computer import Computer
from Database import Database
from Directory import Directory
from MessageBox import MessageBox
from ChatSession import ChatSession

from threading import Thread
from datetime import datetime

# Handle keyboard interrupt shortcuts
def signal_handler(signum, frame):
    pass # prevent exiting
#signal.signal(signal.SIGTSTP, signal_handler)  # Disable Ctrl-Z
#signal.signal(signal.SIGINT, signal_handler)   # Disable Ctrl-C

def main():
    gc.clear()

    print('\n\tWelcome to Hack the Planet!')

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
def profile(user, new_login = False):
    user.show_summary()
    gc.info('Enter \'help\' for a list of commands.\n')
    if new_login: # update last login timestamp if user just logged in
        user.new_login()
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
    profile(user, new_login = True)

# Register a new user account
def register():
    user = User()
    user.register()
    profile(user, new_login = True)

# Establish a connection to IRC
def show_chat(user):
    print('Connecting to chat server...')
    cs = ChatSession(user.handle)
    profile(user)

# Prompt the user for input and respond accordingly.
def prompt(user):
    # enable bash-like input navigation
    cmd_file = os.path.join(os.path.expanduser('~/htp-log'), user.name)
    try:
        readline.read_history_file(cmd_file)
        readline.set_history_length = 100
    except Exception:
        pass

    atexit.register(readline.write_history_file, cmd_file)

    db = Database()
    directory = user.get_home_dir() # start in home directory

    show_prompt = True
    while show_prompt:
        cmd_str = raw_input(user.handle + '@localhost:' + directory.fullpath + '$ ').lower()
        cmds = cmd_str.split()
        base_cmd = cmds[0]
        if base_cmd == 'help':
            gc.msg('Command list:')
            gc.msg('- [chat] - opens chat room')
            gc.msg('- [ls|dir] - shows objects in current directory')
            gc.msg('- [cd <dest>] - changes directory to <dest>; use .. to go up one level')
            gc.msg('- [edit <file>] - starts text editor for <file>')
            gc.msg('- [view|cat <file>] - outputs the contents of <file>')
            gc.msg('- [md|mkdir <dir>] - creates a new directory <dir>')
            gc.msg('- [mf|mkfile <file>] - creates a new file <file>')
            gc.msg('- [rm|del <object>] - permanently deletes <object> and its contents')
            gc.msg('- [disk] - shows information about disk usage')
        elif base_cmd == 'chat':
            show_chat(user)

        # create a new directory
        elif base_cmd in ['md', 'mkdir']:
            if len(cmds) > 1:
                dir_name = cmds[1]
                # check if name is valid
                if not dir_name.isalnum():
                    gc.error('Directory names can only contain letters and numbers.')
                elif len(dir_name) > gc.DIR_MAX_LENGTH:
                    gc.error('Directory names can contain at most ' + str(gc.DIR_MAX_LENGTH) + ' characters.')
                else:
                    # check if name is already taken
                    d = Directory(dir_name, directory.id)
                    d.lookup()
                    if d.exists:
                        gc.error('That directory already exists here.')
                    elif False:
                        # check if there is enough room on the disk
                        pass
                    elif directory.nesting > gc.DIR_MAX_NEST:
                        # check if the nesting level is too deep
                        gc.error('Sorry, directories can be nested more than ' + str(gc.DIR_MAX_NEST) + ' deep.')

                    else:
                        # create the directory
                        d.username = user.name
                        d.parent_name = directory.name
                        d.comp_id = user.computer.id
                        d.save()
                        gc.msg('New directory ' + dir_name + ' successfully created.')
            else:
                # show command usage
                gc.msg('Enter md [dir] to create a new directory named [dir].')

        # create a new file
        elif base_cmd in ['mf', 'mkfile']:
            if len(cmds) > 1:
                f_name = cmds[1] + '.txt'
                # check if name is valid
                if not cmds[1].isalnum():
                    gc.error('File names can only contain letters and numbers.')
                    gc.warning('Note that .txt will be automatically appended to your filename.')
                elif len(f_name) > gc.FILE_MAX_LENGTH:
                    gc.error('File names can contain at most ' + str(gc.FILE_MAX_LENGTH) + 'characters.')
                else:
                    # check if name is already taken
                    file = File(f_name, directory)
                    file.lookup()
                    if file.exists:
                        gc.error('That file already exists here.')
                    else:
                        file.save()
                        gc.success('File ' + f_name + ' created successfully.')
            else:
                # show command usage
                gc.msg('Enter mf [file] to create a new text file named [file].txt')

        # remove a directory
        elif base_cmd in ['rm', 'del']:
            if len(cmds) > 1:
                obj_name = cmds[1]

                # check if entered name matches a file
                file = File(obj_name, directory)
                file.lookup()
                if file.exists:
                    file.delete()
                elif obj_name == '~':
                    gc.error('You cannot delete the home directory.')
                elif obj_name == '.':
                    gc.error('You cannot delete the directory you are currently in.')
                else:
                    # check if entered name matches a directory
                    d = Directory(obj_name, directory.id)
                    d.lookup()
                    if d.exists:
                        confirm = raw_input('Really delete directory ' + obj_name + '? (Y/N): ')
                        if confirm.lower() == 'y':
                            d.delete()
                            gc.success('Deleted directory ' + obj_name)
                        else:
                            gc.warning('Directory ' + obj_name + ' was not deleted')
                    else:
                        gc.error('That object does not exist here.')
            else:
                # show command usage
                gc.msg('Enter rm [object] to permanently delete a file or directory.')

        # show objects in current directory
        elif base_cmd in ['ls', 'dir']:
            directory.print_contents()

        # change directory
        elif base_cmd == 'cd':
            if len(cmds) > 1:
                new_dir = Directory()
                # get parent directory if user entered 'cd ..'
                if cmds[1] == '..':
                    new_dir.id = directory.parent_id
                    new_dir.lookup()
                    if directory.name == '~':
                        gc.error('You are already in the top directory.')
                    elif new_dir.exists:
                        directory = new_dir
                    else:
                        gc.report(1)
                elif cmds[1] == '~':
                    directory = user.get_home_dir()
                else:
                    new_dir.name = cmds[1]
                    new_dir.parent_id = directory.id
                    if not new_dir.name.isalnum():
                        gc.error('Directories can only contain letters and numbers.')
                    else:
                        new_dir.lookup()
                        if new_dir.exists:
                            directory = new_dir
                        else:
                            gc.error('That directory doesn\'t exist.')
            else:
                # show command usage
                gc.msg('Enter cd [dir] to change to a folder named [dir].')
                gc.msg('You can also use cd .. to go up one level,')
                gc.msg('or cd ~ to go to the root directory.')

        # show disk info
        elif base_cmd == 'disk':
            user.computer.print_disk_info()

        # show contents of file
        elif base_cmd in ['view', 'cat']:
            if len(cmds) > 1:
                f_name = cmds[1]
                f = File(f_name, directory)
                f.lookup()
                if f.exists:
                    f.print_contents()
                else:
                    # check if file exists after adding '.txt'
                    f_name += '.txt'
                    f = File(f_name, directory)
                    f.lookup()
                    if f.exists:
                        f.print_contents()
                    else:
                        gc.error('That file doesn\'t exist here.')
            else:
                # show command usage
                gc.msg('Enter view [file] to view the contents of [file].')

        # show general info about an object
        elif base_cmd == 'info':
            if len(cmds) > 1:
                # check for file with matching name
                name = cmds[1]
                f = File(name, directory)
                f.lookup()

                if name == '.':
                    directory.print_info()
                elif name == '~':
                    user.get_home_dir().print_info()
                elif f.exists:
                    f.print_info()
                else:
                    d = Directory(name, directory.id)
                    d.lookup()
                    if d.exists:
                        d.print_info()
                    else:
                        gc.error('That file doesn\'t exist here.')
            else:
                # show command usage
                gc.msg('Get general info about an object by typing info [object].')

        # exit the game (TODO: remove this for production)
        elif base_cmd == 'exit':
            show_prompt = False
            # exit script and disconnect from server
            exit()

        # command not found
        else:
            gc.error('Sorry, your input was not understood. Enter help for a list of commands.')

    # close database
    db.close()

# Prompt for a numeric input
def prompt_num():
    return raw_input('\n# ')

if __name__ == '__main__':
    main()
