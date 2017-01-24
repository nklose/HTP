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
    user.profile()

# Establish a connection to IRC
def show_chat(user):
    print('Connecting to chat server...')
    cs = ChatSession(user.handle)
    profile(user)

# Prompt the user for input and respond accordingly.
def prompt(user):
    db = Database()
    directory = Directory(user.name, '~') # start in home directory
    directory.lookup()

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
            gc.msg('- [view <file>] - outputs the contents of <file>')
            gc.msg('- [md|mkdir <dir>] - creates a new directory <dir>')
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
                    taken = False
                    for file in directory.files:
                        if file.name == dir_name:
                            gc.error('That directory already exists here.')
                            taken = True
                    if not taken:
                        # check if there is enough room on the disk
                        # check if the nesting level is too deep
                        if directory.nesting > gc.DIR_MAX_NEST:
                            gc.error('Sorry, directories can be nested more than ' + str(gc.DIR_MAX_NEST) + ' deep.')
                        # create the directory
                        else:
                            new_dir = Directory(user.name, dir_name, directory.id, directory.name, user.computer.id)
                            new_dir.save()
                            gc.msg('New directory ' + dir_name + ' successfully created.')
            else:
                # show command usage
                gc.msg('Enter md [dir] to create a new directory named [dir].')

        # remove a directory
        elif base_cmd in ['rm', 'del']:
            if len(cmds) > 1:
                obj_name = cmds[1]
                deleted = False
                exists = False
                # check if file exists
                for file in directory.files:
                    if obj_name == file.name: 
                        # delete the file
                        file = File(obj_name, directory)
                        file.delete()
                        deleted = True
                        exists = True
                        gc.success('Deleted file ' + obj_name)
                if not deleted:
                    for subdir in directory.subdirs:
                        if obj_name == subdir.name:
                            # delete the subdirectory
                            exists = True
                            subdir = Directory(obj_name, parent_id = directory.id)
                            confirm = raw_input('Really delete directory ' + obj_name + '? (Y/N): ')
                            if confirm.lower() == 'y':
                                subdir.delete()
                                deleted = True
                                gc.success('Deleted directory ' + obj_name)
                            else:
                                gc.warning('Directory ' + obj_name + ' was not deleted')

                directory.lookup()

                if not exists:
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
                    new_dir.name = '~'
                    new_dir.username = user.name
                    new_dir.lookup()
                    if new_dir.exists:
                        directory = new_dir
                    else:
                        gc.report(2)
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
