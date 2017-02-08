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
    return raw_input('\n# ')

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
            mb.add_property('processes (ps)', 'shows your running processes')
            mb.add_heading('Networking')
            mb.add_property('ping <target>', 'sends an echo request to the IP or domain <target>')
            mb.add_property('ssh <target>', 'attempts to log into IP or domain <target>')
            mb.add_property('ul (upload) <path>', 'uploads the object at local path <path>')
            mb.add_property('dl (download) <obj>', 'downloads the object <obj> to ~/downloads')
            mb.display()
        elif base_cmd == 'chat':
            # switches to chat mode
            print('Connecting to chat server...')
            cs = ChatSession(user.handle)

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
                        log_entry = user.handle + ' created directory ' + dir_name
                        computer.add_log_entry(log_entry)
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
                        log_entry = user.handle + ' created file ' + f_name
                        computer.add_log_entry(log_entry)
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

        elif base_cmd == 'edit':
            if len(cmds) > 1:
                f_name = cmds[1]
                f = File(f_name, directory)
                f.lookup()
                if f.exists:
                    # edit file in text editor
                    TextEditor(f)
                    if gc.prompt_yn('Do you want to save your changes to the file?'):
                        f.save()
                        gc.success('File saved successfully.')
                        if not f.is_log_file():
                            log_entry = user.handle + ' edited file ' + f.parent.fullpath + '/' + f.name
                            computer.add_log_entry(log_entry)

                    else:
                        gc.warning('File not saved.')
                else:
                    gc.error('That file doesn\'t exist here.')
                    gc.warning('If the file is new, please create it first with \'mf\'.')
            else:
                # show command usage
                gc.msg('Enter edit [file] to start editing a text file.')

        # moves an object to a new directory
        elif base_cmd in ['mv', 'move']:
            pass

        # renames an object
        elif base_cmd in ['rn', 'rename']:
            pass

        # copies an object
        elif base_cmd in ['cp', 'copy']:
            pass

        # show disk info
        elif base_cmd == 'disk':
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
                    time.sleep(1)
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
                            password = raw_input('  Password: ')
                            time.sleep(1)
                            if password == c.password:
                                gc.success('Connected to ' + target + '.\n')
                                c.show_login_banner()
                                correct = True
                                computer = c
                                directory = c.root_dir
                                log_entry = 'new remote session for ' + user.handle + ' [' + user.computer.ip + ']'
                                computer.add_log_entry(log_entry)
                            else:
                                gc.error('Invalid credentials. Attempt ' + str(attempts) + ' of 3.')
                                computer.add_log_entry('root login failed')
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
                        time.sleep(1)
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
            pass

        # uploads a file
        elif base_cmd in ['ul', 'upload']:
            pass

        # change a property for a user's account
        elif base_cmd == 'set':
            if len(cmds) > 1:
                pass
            else:
                # show command usage
                gc.msg('This can be used to change settings for your account.')
                gc.msg('Valid settings: email, handle')

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
                binfile = File(cmds[1], computer.root_dir)
                binfile.lookup()
                if binfile.exists:
                    binfile.run()
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
            mb.set_title('Running processes for ' + user.handle + ':')

            db = Database()
            sql = 'SELECT * FROM processes WHERE user_id = %s'
            args = [user.id]
            results = db.get_query(sql, args)
            for result in results:
                pr_id = int(result[0])
                comp_id = int(result[1])
                file_id = int(result[2])
                started_on = result[4]
                finished_on = result[5]
                memory = int(result[6])

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
                process = Process(id = pr_id)
                process.lookup()
                seconds = process.get_time_remaining()
                remaining = gc.hr_seconds(seconds)

                # add to message box
                property_str = 'on ' + comp.ip + ' (' + str(memory) + ' MB) '
                property_str += 'with ' + remaining + ' remaining'
                mb.add_property(file.name, property_str)

            db.close()
            mb.display()

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