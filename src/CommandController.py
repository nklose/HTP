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

# File: CommandController.py
# The command controller handles processing of user-inputted commands.

import os
import re
import time
import string
import atexit
import random
import datetime
import readline
import subprocess

import GameController as gc

from User import User
from File import File
from Process import Process
from Computer import Computer
from Database import Database
from Directory import Directory
from MessageBox import MessageBox
from TextEditor import TextEditor
from ChatSession import ChatSession

# Prompt for a numeric input
def prompt_num():
    return raw_input('\n#: ')

# Prompt the user for input and respond accordingly.
def prompt(user):
    # enable bash-like input navigation
    cmd_file = os.path.join(gc.CMD_LOG_DIR, user.name + '.log')
    try:
        readline.read_history_file(cmd_file)
        readline.set_history_length = gc.CMD_LOG_LENGTH
    except Exception:
        pass
    atexit.register(readline.write_history_file, cmd_file)

    # initialize the database
    db = Database()

    # start user in home directory on login
    computer = user.computer
    directory = user.get_home_dir()

    # begin command processing
    show_prompt = True
    while show_prompt:
        # get user input
        hostname = ''
        if computer == user.computer:
            hostname = 'localhost'
        else:
            hostname = computer.ip
        cmd_str = raw_input(user.handle + '@' + hostname + ':' + directory.fullpath + '$ ').lower()

        # split into separate strings
        cmds = cmd_str.split()

        # save first entered string as base command (other strings are parameters)
        base_cmd = []
        if len(cmds) > 0:
            base_cmd = cmds[0]

        # display help info
        if base_cmd == 'help':
            gc.show_help()

        # switch to chat mode
        elif base_cmd == 'chat':
            print('Connecting to chat server...')
            cs = ChatSession(user.handle)

        # create a new directory
        elif base_cmd in ['md', 'mkdir']:
            if len(cmds) > 1:
                dir_name = cmds[1]
                computer.check_space()
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
                    # check if parent directory is read-only
                    elif directory.read_only:
                        gc.error('The current directory is marked as read-only.')
                    # check if there is enough room on the disk
                    elif computer.disk_free < gc.DIR_SIZE:
                        gc.error('There is not enough free disk space to create a new directory.')
                    # check if the nesting level is too deep
                    elif directory.nesting > gc.DIR_MAX_NEST:
                        gc.error('Sorry, directories can be nested more than ' + str(gc.DIR_MAX_NEST) + ' deep.')
                    # check if the max number of directories exist already
                    elif computer.get_dir_count() >= gc.DIR_MAX_COUNT:
                        gc.error('Sorry, the filesystem will not support additional directories.')
                    else:
                        # create the directory
                        d.username = user.name
                        d.parent_name = directory.name
                        d.comp_id = user.computer.id
                        d.save()
                        gc.msg('New directory ' + dir_name + ' successfully created.')
                        log_entry = user.handle + ' created directory ' + dir_name
                        computer.add_log_entry(log_entry)
            else:
                # show command usage
                gc.msg('Enter md [dir] to create a new directory named [dir].')

        # create a new file
        elif base_cmd in ['mf', 'mkfile']:
            if len(cmds) > 1:
                base_name = cmds[1]

                if base_name[-4:] == '.txt': # strip file name if necessary
                    base_name = base_name[:-4]

                if base_name[-4] == '.': # reject other file extensions
                    gc.error('You can only create new files ending in .txt.')
                else:
                    f_name = base_name + '.txt' # add file extension
                    computer.check_space()      # update available space on computer

                    if not base_name.isalnum(): # check if name is alphanumeric
                        gc.error('File names can only contain letters and numbers.')
                    elif len(f_name) > gc.FILE_MAX_LENGTH: # check if name is too long for filesystem
                        gc.error('File names can contain at most ' + str(gc.FILE_MAX_LENGTH) + 'characters.')
                    elif directory.read_only: # check if parent is read-only
                            gc.error('The current directory is marked as read-only.')
                    else:
                        file = File(f_name, directory)
                        file.lookup()
                        if file.exists: # check if name is already taken
                            gc.error('That file already exists here.')
                        elif computer.disk_free < file.size: # check if disk is full
                            gc.error('There isn\'t enough room on the disk for this file.')
                        else:
                            file.save()
                            gc.success('File ' + f_name + ' created successfully.')
                            log_entry = user.handle + ' created file ' + f_name
                            computer.add_log_entry(log_entry)
            else:
                # show command usage
                gc.msg('Enter mf [file] to create a new text file named [file].txt')

        # remove a directory
        elif base_cmd in ['rm', 'del']:
            if len(cmds) > 1:
                for obj_name in cmds[1:]:
                    # check if entered name matches a file
                    file = File(obj_name, directory)
                    file.lookup()
                    if file.is_live and not file.owner_id == user.id:
                        gc.warning('You don\'t have permission to delete that file.')
                    elif file.exists:
                        file.delete()
                        gc.success('Deleted file ' + obj_name)
                        if obj_name != 'log.txt':
                            log_entry = user.handle + ' deleted file ' + obj_name
                            user.computer.add_log_entry(log_entry)
                    elif obj_name == '~':
                        gc.error('You cannot delete the home directory.')
                    elif obj_name == '.':
                        gc.error('You cannot delete the directory you are currently in.')
                    else:
                        # check if entered name matches a directory
                        d = Directory(obj_name, directory.id)
                        d.lookup()
                        if d.exists:
                            if gc.prompt_yn('Really delete directory ' + obj_name + '?'):
                                d.delete()
                                gc.success('Deleted directory ' + obj_name)
                                log_entry = user.handle + ' deleted directory ' + obj_name
                                computer.add_log_entry(log_entry)
                            else:
                                gc.warning('Directory ' + obj_name + ' was not deleted')
                        else:
                            gc.error('That object does not exist here.')
            else:
                # show command usage
                gc.msg('Enter rm [object] to permanently delete a file or directory.')

        # show objects in current directory
        elif base_cmd in ['ls', 'dir']:
            if len(cmds) > 1:
                ls_dir = directory.navigate(cmds[1])
                if not ls_dir.id == directory.id:
                    ls_dir.print_contents()
            else:
                directory.print_contents()

        # change directory
        elif base_cmd == 'cd':
            if len(cmds) > 1:
                directory = directory.navigate(cmds[1])
            else:
                # show command usage
                gc.msg('Enter cd [path] to change to the directory at the specified path.')
                gc.msg('Use .. for \'up one level\' or ~ for \'top directory\'.')
                gc.msg('e.g. \'cd ../os\' goes up one level and then to the \'os\' directory.')

        elif base_cmd == 'edit':
            if len(cmds) > 1:
                objects = cmds[1].split('/')            # entered filepath
                dirs = string.join(objects[:-1], '/')   # list of directories to navigate through
                f_name = objects[-1]                    # name of the file to edit
                f_dir = directory.navigate(dirs)

                if f_dir.read_only:
                    gc.error('The file you specified is in a read-only directory and cannot be edited.')
                elif f_dir.exists:
                    f = File(f_name, f_dir)
                    f.lookup()
                    if f.exists:
                        TextEditor(f)
                        if gc.prompt_yn('Do you want to save your changes to the file?'):
                            f.save()
                            gc.success('File saved successfully.')
                            user.increment_stat('files_edited')
                            if not f.is_log_file():
                                log_entry = user.handle + ' edited file ' + f.parent.fullpath + '/' + f.name
                                computer.add_log_entry(log_entry)
                        else:
                            gc.warning('File not saved.')
                    else:
                        gc.error('That file doesn\'t exist.')
                else:
                    gc.error('You entered an invalid directory path.')

            else:
                # show command usage
                gc.msg('Enter edit [file] to start editing a text file.')

        # moves an object to a new directory
        elif base_cmd in ['mv', 'move']:
            if len(cmds) > 2:
                obj_name = cmds[1]
                dir_path = cmds[2]
                file = File(obj_name, directory)
                file.lookup()
                new_dir = directory.navigate(dir_path)
                if file.exists:
                    if new_dir.id != directory.id:
                        file.parent = new_dir
                        file.save()
                        gc.success('File moved successfully.')
                    else:
                        gc.error('The destination directory doesn\'t exist.')
                else:
                    d = Directory(obj_name, directory.id)
                    d.lookup()
                    if d.exists:
                        if new_dir.id != directory.id:
                            d.parent_id = new_dir.id
                            d.save()
                            gc.success('Directory moved successfully.')
                        else:
                            gc.error('The destination directory doesn\'t exist.')
                    else:
                        gc.error('The object you entered doesn\'t exist here.')
            else:
                # show command usage
                gc.msg('Enter mv [file] [folder] to move a file to a new folder.')

        # renames an object
        elif base_cmd in ['rn', 'rename']:
            if len(cmds) > 2:
                obj_name = cmds[1]
                new_name = cmds[2]

                # check if object is a file
                file = File(obj_name, directory)
                file.lookup()
                if file.exists:
                    newfile = File(new_name, directory)
                    newfile.lookup()
                    if newfile.exists: # check if a file already exists with the new name
                        gc.error('A file already exists here with the new name you specified.')
                    elif not gc.valid_filename(new_name): # check if name is valid
                        gc.error('File names can only contain letters, numbers, dots, dashes, and underscores.')
                    elif new_name[-4:] != obj_name[-4:]: # check if extensions match
                        gc.error('The new file extension must match the old one.')
                    else:
                        file.name = new_name
                        file.save()
                        gc.success('File renamed successfully.')
                # check if object is a directory
                else:
                    d = Directory(obj_name, directory.id)
                    d.lookup()
                    if d.exists:
                        newdir = Directory(new_name, directory.id)
                        newdir.lookup()
                        if newdir.exists: # check if a directory already exists with the new name
                            gc.error('A directory already exists here with the new name you specified.')
                        elif not gc.valid_dirname(new_name): # check if name is valid
                            gc.error('Directory names can only contain letters, numbers, dashes, and underscores.')
                        else:
                            d.name = new_name
                            d.save()
                            gc.success('Directory renamed successfully.')
                    else:
                        gc.error('The object you entered doesn\'t exist here.')
            else:
                # show command usage
                gc.msg('Enter rn [object] [newname] to rename a file or directory.')

        # copies an object
        elif base_cmd in ['cp', 'copy']:
            if len(cmds) > 2:
                obj_name = cmds[1]
                new_name = cmds[2]

                # check if object is a file
                file = File(obj_name, directory)
                file.lookup()
                if file.exists:
                    newfile = File(new_name, directory)
                    newfile.lookup()
                    if newfile.exists:
                        gc.error('A file already exists here with the name you specified.')
                    else:
                        newfile.copy(file)
            else:
                # show command usage
                gc.msg('Enter cp [object] [newname] to copy a file or directory.')

        # show disk info
        elif base_cmd == 'disk':
            computer.lookup()
            computer.print_disk_info()
            if gc.prompt_yn('List all disk contents?'):
                computer.print_all_contents()

        # show log file
        elif base_cmd == 'log':
            computer.print_log_file()

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

        # attempts SSH login on target
        elif base_cmd == 'ssh':
            if len(cmds) > 1:
                target = cmds[1]
                gc.msg('Attempting SSH connection to ' + target + '...')
                if target in ['127.0.0.1', 'localhost']:
                    gc.warning('You are already connected.')
                else:
                    # attempt lookup via IP
                    c = Computer()
                    c.ip = target
                    c.lookup()
                    if not c.exists:
                        # attempt lookup via domain
                        c = Computer()
                        c.domain = target
                        c.lookup()

                    if c.exists:
                        gc.warning('Beginning authorization...')
                        attempts = 1
                        correct = False
                        while attempts <= 3 and not correct:
                            password = gc.prompt('Password')
                            if password == c.password:
                                gc.success('Connected to ' + target + '.\n')
                                c.show_login_banner()
                                correct = True
                                computer = c
                                directory = c.root_dir
                                log_entry = 'new remote session for ' + user.handle + ' [' + user.computer.ip + ']'
                                computer.add_log_entry(log_entry)
                                user.increment_stat('ssh_count')
                            else:
                                gc.error('Invalid credentials. Attempt ' + str(attempts) + ' of 3.')
                                computer.add_log_entry('root login failed')
                                time.sleep(1)
                            attempts += 1
                    else:
                        gc.error('Unable to connect to ' + target + '.')

            else:
                # show command usage
                gc.msg('Establish a connection to the target by typing [ssh] target.')
                gc.msg('You will need a valid password to connect.')

        # pings the specified IP or domain
        elif base_cmd == 'ping':
            if len(cmds) > 1:
                # TODO: add regex match for IP/domain
                target = cmds[1]
                gc.msg('Pinging ' + target + '...')

                if target in ['127.0.0.1', 'localhost']:
                    i = 0
                    while i < 3:
                        time.sleep(1)
                        gc.success('  Reply from ' + target + ' (time < 1 ms)')
                        i += 1
                else:
                    # check for a matching domain or IP
                    c1 = Computer()
                    c1.ip = target
                    c1.lookup()
                    c2 = Computer()
                    c2.domain = target
                    c2.lookup()

                    i = 0
                    latency = random.randint(10, 100) # simulate ping delay
                    while i < 3:
                        time.sleep(0.5)
                        i += 1
                        if c1.exists or c2.exists:
                            ms = str(latency + random.randint(0, 10)) + ' ms'
                            reply = '  Reply from ' + target
                            if c2.exists: # 'resolve' domain if possible
                                reply += ' [' + c2.ip + ']'
                            reply += ' (time: ' + ms + ')'
                            gc.success(reply)

                        else:
                            gc.warning('  Request timed out.')

            else:
                # show command usage
                gc.msg('Send an echo request to a target IP or domain by typing ping [target]')

        # downloads a file
        elif base_cmd in ['dl', 'download']:
            if len(cmds) > 1:
                if computer != user.computer:
                    for fname in cmds[1:]:
                        file = File(fname, directory)
                        file.lookup()
                        if file.exists:
                            user.computer.check_space()
                            if file.size + gc.DIR_SIZE > user.computer.disk_free:
                                gc.error('Your computer doesn\'t have enough free space to download this.')
                            elif file.is_live:
                                gc.error('You can\'t download a live program.')
                            else:
                                dl_dir = Directory('downloads', user.computer.root_dir.id)
                                dl_dir.lookup()
                                if not dl_dir.exists:
                                    dl_dir.save()
                                    dl_dir.lookup()
                                newfile = File(file.name, dl_dir)
                                newfile.owner_id = user.id
                                newfile.content = file.content
                                newfile.type = file.type
                                newfile.size = file.size
                                newfile.category = file.category
                                newfile.comment = file.comment
                                newfile.memory = file.memory
                                newfile.save()
                                gc.success('File ' + newfile.name + ' downloaded to ~/downloads.')

                        else:
                            gc.error('That file doesn\'t exist here.')
                else:
                    gc.warning('This file is already on your computer, so you can\'t download it.')
            else:
                # show comand usage
                gc.msg('Download a file to your computer by typing dl [file].')

        # uploads a file
        elif base_cmd in ['ul', 'upload']:
            pass

        # change a property for a user's account
        elif base_cmd == 'set':
            if len(cmds) > 1:
                if cmds[1] == 'email':
                    user.change_email()
                elif cmds[1] == 'handle':
                    user.change_handle()
                elif cmds[1] == 'password':
                    user.change_password()
                elif cmds[1] == 'ip':
                    gc.warning('Use the command chip to change your ip.')
            else:
                # show command usage
                gc.msg('This can be used to change settings for your account.')
                gc.msg('Valid settings: email, handle, password')

        # validate an email address with a given token
        elif base_cmd == 'verify':
            if len(cmds) > 1:
                if user.email_confirmed:
                    gc.warning('Your email address has already been confirmed.')
                    gc.msg('If you want to change your email, type \'set email\'.')
                elif cmds[1] == 'resend':
                    user.confirm_email()
                elif cmds[1] == user.token:
                    user.lookup()
                    # check if the token is still valid
                    if user.token_date > gc.string_to_ts(gc.current_time()) - datetime.timedelta(days = 1):
                        user.token = ''
                        user.email_confirmed = True
                        user.save()
                        gc.success('Thanks, your email address has been confirmed.')
                    else:
                        gc.error('Sorry, that token has expired.')
                        gc.msg('To resend the verification email, type \'verify resend\'.')
                else:
                    gc.error('Sorry, the token you entered is invalid.')
                    gc.msg('If you want to resend the verification email, type \'verify resend\'.')
                    gc.msg('To change the email linked to your account, type \'set email\'.')
            else:
                # show command usage
                gc.msg('This command is used to verify an email address with a given token.')
                gc.msg('If you want to resend the verification email, type \'verify resend\'.')
                gc.msg('To change the email linked to your account, type \'set email\'.')

        # executes a program
        elif base_cmd == 'run':
            if len(cmds) > 1:
                binfile = File(cmds[1], directory)
                binfile.lookup()
                if binfile.exists:
                    user.run_program(binfile)
                else:
                    gc.error('That program doesn\'t exist here.')
            else:
                # show command usage
                gc.msg('Enter \'run <file>\' to execute a binary program.')

        # shows the user login summary
        elif base_cmd == 'summary':
            user.show_summary()

        # show running processes
        elif base_cmd in ['ps', 'processes']:
            mb = MessageBox()
            mb.set_label_width(32)
            mb.set_title('Running processes for ' + user.handle + ':')

            db = Database()
            sql = 'SELECT * FROM processes WHERE user_id = %s'
            args = [user.id]
            results = db.get_query(sql, args)
            i = 1
            for result in results:
                pr_id = int(result[0])
                comp_id = int(result[1])
                file_id = int(result[2])
                user_id = int(result[3])
                target_id = -1
                if not result[4] == None:
                    target_id = int(result[4])
                started_on = result[5]
                finished_on = result[6]
                memory = int(result[7])

                # get file object
                sql = 'SELECT * FROM files WHERE id = %s'
                args = [file_id]
                file_result = db.get_query(sql, args)
                file_name = file_result[0][1]
                parent_id = int(file_result[0][2])
                parent = Directory(id = parent_id)
                parent.lookup()
                file = File(file_name, parent)
                file.lookup()

                # get computer object
                comp = Computer(id = comp_id)
                comp.lookup()

                # get time remaining
                process = Process(computer = user.computer, user = user, id = pr_id)
                process.lookup()
                seconds = process.get_time_remaining()
                remaining = gc.hr_seconds(seconds)

                # add to message box
                property_str = ''
                remaining_str = ' (' + remaining + ' remaining)'
                if seconds <= 0:
                    remaining_str = ' (COMPLETE)'

                if process.target != None:
                    property_str = 'against ' + process.target.ip + remaining_str
                else:
                    property_str = 'on ' + comp.ip + remaining_str

                mb.add_property(str(i) + ': ' + file.name + ' (' + str(memory) + ' MB)', property_str)
                i += 1
            db.close()
            mb.display()

        # finish a process
        elif base_cmd in ['stop', 'close', 'finish']:
            if len(cmds) > 1:
                try:
                    pindex = int(cmds[1])
                    db = Database()
                    sql = 'SELECT * FROM processes WHERE user_id = %s'
                    args = [user.id]
                    results = db.get_query(sql, args)
                    pr_result = results[pindex - 1]
                    pr_id = int(pr_result[0])
                    if len(pr_result) > 0 and pindex > 0:
                        process = Process(computer = user.computer, user = user, id = pr_id)
                        process.lookup()
                        if process.exists:
                            seconds = process.get_time_remaining()
                            if seconds > 0:
                                gc.warning('That process hasn\'t finished yet.')
                                if gc.prompt_yn('  Close anyway?'):
                                    process.stop()
                                    gc.success('Process stopped.')
                                else:
                                    gc.warning('Process will continue running.')
                            else:
                                gc.success('Closing process #' + str(pindex) + '.')
                                user.finish_process(process)
                        else:
                            gc.error('A problem occurred while checking the process.')
                    else:
                        gc.error('That process couldn\'t be found. Please enter the ID of a valid process.')
                    db.close()
                except Exception as e:
                    gc.error('That process couldn\'t be found. Please enter the ID of a valid process.')
            else:
                # show command usage
                gc.msg('Enter close <process_id> to finish a process.')
                gc.msg('Enter processes to see a list of all active processes.')

        elif base_cmd in ['res', 'resources']:
            computer.show_resources()

        elif base_cmd == 'stats':
            user.show_stats()

        # exit the game (TODO: remove this for production)
        elif base_cmd in ['exit', 'quit']:
            if computer == user.computer:
                gc.msg('Disconnecting from localhost...')
                show_prompt = False
                # exit script and disconnect from server
                exit()
            else:
                gc.msg('Disconnecting from ' + computer.ip + '...')
                computer = user.computer
                directory = user.get_home_dir()

        # command not found
        else:
            gc.error('Sorry, your input was not understood. Enter help for a list of commands.')

    # close database
    db.close()