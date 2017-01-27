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
import atexit
import readline
import subprocess

import GameController as gc

from User import User
from File import File
from Database import Database
from Directory import Directory
from MessageBox import MessageBox
from TextEditor import TextEditor

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
    directory = user.get_home_dir()

    # begin command processing
    show_prompt = True
    while show_prompt:
        # get user input
        cmd_str = raw_input(user.handle + '@localhost:' + directory.fullpath + '$ ').lower()

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
            mb.set_label_width(20)
            mb.add_property('chat', 'opens the globalchat room')
            mb.add_property('ls (dir)', 'lists objects in the current directory')
            mb.add_property('cd <dir>', 'jumps to the directory <dir>')
            mb.add_property('edit <file>', 'starts text editor for <file>')
            mb.add_property('view (cat) <file>', 'outputs the contents of <file>')
            mb.add_property('md (mkdir) <name>', 'creates a new directory called <name>')
            mb.add_property('mf (mkfile) <name>', 'creates a new test file called <name>')
            mb.add_property('rm (del) <obj>', 'permanently deletes <obj> and its contents')
            mb.add_property('disk', 'shows information about disk usage')
            mb.display()
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
                        log_entry = user.handle + ' created directory ' + dir_name
                        user.computer.add_log_entry(log_entry)
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
                        user.computer.add_log_entry(log_entry)
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
                            user.computer.add_log_entry(log_entry)
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
                        log_entry = user.handle + ' edited file ' + f.parent.fullpath + '/' + f.name
                        user.computer.add_log_entry(log_entry)
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

        # downloads a file
        elif base_cmd in ['dl', 'download']:
            pass

        # uploads a file
        elif base_cmd in ['ul', 'upload']:
            pass

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