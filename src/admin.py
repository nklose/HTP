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

# File: admin.py
# This is the administrative interface for the game.
# It can be used to monitor and modify the game in realtime.

import os
import atexit
import readline

import GameController as gc

from File import File
from User import User
from Computer import Computer
from Database import Database
from Directory import Directory
from MessageBox import MessageBox

def main():
    cmd_file = os.path.join(gc.CMD_LOG_DIR, 'admin.log')
    try:
        readline.read_history_file(cmd_file)
        readline.set_history_length = gc.CMD_LOG_LENGTH
    except Exception:
        pass
    atexit.register(readline.write_history_file, cmd_file)

    gc.msg('Welcome to the HTP Admin Control Panel.')
    gc.info('Type help for a list of commands.')

    show_prompt = True
    while show_prompt:
        # get command
        cmd_str = raw_input('[ADMIN]: ').lower()
        cmds = cmd_str.split()
        base_cmd = []
        if len(cmds) > 0:
            base_cmd = cmds[0]

        # show command list
        if base_cmd == 'help':
            mb = MessageBox()
            mb.set_title('Admin Command List')
            mb.add_heading('Basic Commands')
            mb.add_property('stats', 'shows basic game statistics')
            mb.add_property('exit (quit)', 'exits the HTP Admin Control Panel')
            mb.add_property('create <obj>', 'creates something (npc, user)')
            mb.add_property('delete <obj>', 'deletes something (computer, user, npc)')
            mb.add_property('show <obj>', 'shows details about something (computer[s], user[s], npc[s])')
            mb.add_property('disk <CompID>', 'shows info and contents about a computer\'s disk')
            mb.display()

        # show game statistics
        elif base_cmd == 'stats':
            # collect stats
            db = Database()

            sql = 'SELECT COUNT(*) FROM users'
            users_total = db.get_query(sql)[0][0]
            sql = 'SELECT COUNT(*) FROM users WHERE last_login > now() - INTERVAL 1 HOUR'
            users_hour = db.get_query(sql)[0][0]
            sql = 'SELECT COUNT(*) FROM users WHERE last_login > now() - INTERVAL 1 DAY'
            users_day = db.get_query(sql)[0][0]
            sql = 'SELECT COUNT(*) FROM users WHERE last_login > now() - INTERVAL 1 MONTH'
            users_month = db.get_query(sql)[0][0]
            sql = 'SELECT COUNT(*) FROM computers WHERE owner_id = 0'
            npcs = db.get_query(sql)[0][0]
            sql = 'SELECT COUNT(*) FROM computers WHERE bank_id IS NOT NULL'
            banks = db.get_query(sql)[0][0]
            sql = 'SELECT COUNT(*) FROM computers WHERE domain_name IS NOT NULL'
            webservers = db.get_query(sql)[0][0]
            db.close()

            # display stats
            mb = MessageBox()
            mb.set_title('Game Statistics')
            mb.add_property('User Count', str(users_total))
            mb.add_property('  (1 Hour)', str(users_hour))
            mb.add_property('  (24 Hours)', str(users_day))
            mb.add_property('  (1 Month)', str(users_month))
            mb.hr()
            mb.add_property('NPC Computers', str(npcs))
            mb.add_property('Bank Servers', str(banks))
            mb.add_property('Web Servers', str(webservers))
            mb.display()

        # create a new object
        elif base_cmd in ['create', 'make', 'new']:
            if len(cmds) > 1:
                if cmds[1] == 'npc':
                    create_npc()
                elif cmds[1] == 'user':
                    user = User()
                    user.register()
                else:
                    gc.error('Sorry, not sure how to create ' + cmds[1] + '.')
            else:
                gc.error('You must specify what you want to create.')

        # deletes an object
        elif base_cmd in ['delete', 'remove', 'del', 'rm']:
            if len(cmds) > 1:
                # computer or NPC
                if cmds[1] in ['computer', 'npc']:
                    if len(cmds) > 2:
                        db = Database()
                        try:
                            c = Computer()
                            c.id = int(cmds[2])
                            c.lookup()
                            if c.exists:
                                sql = 'DELETE FROM computers WHERE id = %s'
                                args = [c.id]
                                db.post_query(sql, args)
                                gc.success('Computer deleted.')
                            else:
                                gc.error('That computer could not be found.')
                        except Exception as e:
                            gc.error('Error: ' + str(e))
                        db.close()
                    else:
                        gc.error('Please specify the ID of the computer/NPC to delete.')
                elif cmds[1] == 'user':
                    if len(cmds) > 2:
                        db = Database()
                        user = User()
                        user.name = cmds[2]
                        user.lookup()
                        if user.exists:
                            sql = 'DELETE FROM users WHERE username = %s'
                            args = [cmds[2]]
                            db.post_query(sql, args)
                            gc.success('User deleted.')
                        else:
                            gc.error('That user could not be found.')
                        db.close()
                    else:
                        gc.error('Please specify the username of the user to delete.')
                else:
                    gc.error('Sorry, not sure how to delete ' + cmds[1] + '.')
            else:
                gc.error('You must specify what you want to delete.')

        # show an object or list of objects
        elif base_cmd == 'show':
            if len(cmds) > 1:
                # all NPCs
                if cmds[1] == 'npcs':
                    show_computers(npcs_only = True)
                # single computer
                elif cmds[1] in ['computer', 'npc']:
                    if len(cmds) > 2:
                        c = Computer()
                        c.id = int(cmds[2])
                        c.lookup()
                        if c.exists:
                            show_computer(c)
                        else:
                            gc.error('Sorry, that computer doesn\'t exist.')
                    else:
                        gc.error('Please specify the ID of the computer to show.')
                # all computers
                elif cmds[1] == 'computers':
                    show_computers()
                # single user
                elif cmds[1] == 'user':
                    if len(cmds) > 2:
                        user = User()
                        user.name = cmds[2]
                        user.lookup()
                        if user.exists:
                            show_user(user)
                        else:
                            gc.error('User not found. Please specify a valid username.')
                    else:
                        gc.error('Please specify the username of the user to show.')
                # all users
                elif cmds[1] == 'users':
                    show_users()
                else:
                    gc.error('Sorry, not sure how to show ' + cmds[1] + '.')
            else:
                gc.error('You must specify what you want to show.')

        # show info and contents for a computer's disk
        elif base_cmd == 'disk':
            if len(cmds) > 1:
                try:
                    c = Computer()
                    c.id = int(cmds[1])
                    c.lookup()
                    if c.exists:
                        show_disk(c)
                    else:
                        gc.error('That computer ID doesn\'t exist.')
                except Exception as e:
                    gc.error('Error: ' + str(e))
            else:
                gc.error('You must specify a computer ID to show its disk info.')

        # load NPC files into database
        elif base_cmd == 'load':
            if len(cmds) > 1:
                if cmds[1] == 'npcs':
                    load_npcs()
                else:
                    gc.error('Sorry, not sure how to load ' + cmds[1] + '.')
            else:
                gc.error('You must specify what you want to load (e.g. npcs)')

        # quit the control panel
        elif base_cmd in ['exit', 'quit']:
            gc.msg('Exiting...')
            show_prompt = False

        # command not understood
        else:
            gc.error('Your input was not understood.')
            gc.info('Type help for a list of commands.')

# adds a new NPC computer to the database and saves its info to a text file
def create_npc():
    gc.msg('Preparing to create a new NPC...')
    c = Computer(0)

    ip = raw_input('\tIP Address (default = random): ')
    if ip != '':
        c.ip = ip

    else:
        c.ip = gc.gen_ip()
    password = raw_input('\tPassword (default = random): ')
    if password != '':
        c.password = password
    else:
        c.password = gc.gen_password()
    domain = raw_input('\tDomain (default = NULL): ')
    if domain != '':
        c.domain = domain
    bank_id = raw_input('\tBank ID (default = NULL): ')
    if bank_id != '':
        c.bank_id = bank_id
    ram = raw_input('\tRAM (default = 512 MB): ')
    if ram != '':
        c.ram = int(ram)
    cpu = raw_input('\tCPU (default = 512 MHz): ')
    if cpu != '':
        c.cpu = int(cpu)
    hdd = raw_input('\tHDD (default = 1 GB): ')
    if hdd != '':
        c.hdd = int(hdd)
    fw_level = raw_input('\tFW Level (default = 0): ')
    if fw_level != '':
        c.fw_level = int(fw_level)
    av_level = raw_input('\tAV Level (default = 0): ')
    if av_level != '':
        c.av_level = int(av_level)
    cr_level = raw_input('\tCR Level (default = 0): ')
    if cr_level != '':
        c.cr_level = int(cr_level)
    c.online = gc.prompt_yn('Is this NPC online?')

    mb = MessageBox()
    mb.set_title('New NPC Information')
    mb.add_property('IP', c.ip)
    mb.add_property('Password', c.password)
    if c.domain != None:
        mb.add_property('Domain', c.domain)
    else:
        mb.add_property('Domain', '')
    mb.add_property('RAM', str(c.ram) + ' MB')
    mb.add_property('CPU', str(c.cpu) + ' MHz')
    mb.add_property('HDD', str(c.hdd) + ' GB')
    mb.add_property('Online', str(c.online))
    mb.display()

    notes = []
    emails = []
    programs = []
    if gc.prompt_yn('Add notes/emails to NPC?'):
        gc.msg('Enter one filename with extension per line.')
        gc.msg('When you are done, enter a blank line.')

        add_more = True
        while add_more:
            note = raw_input('  Filename: ')
            if note == '':
                add_more = False
            elif note[6:] == '.email':
                emails.append(note)
            else:
                notes.append(note)

    if gc.prompt_yn('Add programs to NPC?'):
        gc.msg('When you are done adding programs, enter a blank line.')
        add_more = True
        while add_more:
            fname = raw_input('  Filename: ')
            if fname == '':
                add_more = False
            else:
                programs.append(fname)


    if gc.prompt_yn('Save new NPC to database?'):
        try:
            # save NPC object
            c.save()
            c.lookup()
            gc.success('NPC saved.')
            gc.msg('Writing to file...')
            file = open(os.path.join(gc.NPC_DIR, c.ip + '.npc'), 'w')
            file.write('IP ' + c.ip + '\n')
            file.write('PASSWORD ' + c.password + '\n')
            if c.domain != None:
                file.write('DOMAIN ' + c.domain + '\n')
            if c.bank_id != None:
                file.write('BANK_ID' + c.bank_id + '\n')
            file.write('RAM ' + str(c.ram) + '\n')
            file.write('CPU ' + str(c.cpu) + '\n')
            file.write('HDD ' + str(c.hdd) + '\n')
            file.write('FW_LEVEL ' + str(c.fw_level) + '\n')
            file.write('AV_LEVEL ' + str(c.av_level) + '\n')
            file.write('CR_LEVEL ' + str(c.cr_level) + '\n')
            file.write('ONLINE ' + str(c.online) + '\n')
            
            gc.success('Done.')

            # add note folder if necessary
            if len(notes) > 0:
                gc.msg('Adding notes...')
                note_dir = Directory('notes', c.root_dir.id)
                note_dir.comp_id = c.id
                note_dir.read_only = True
                note_dir.save()
                gc.success('Added directory ' + note_dir.name + '.')
                note_dir.lookup()

                # add notes to folder
                for note in notes:
                    notefile = File(note, note_dir)
                    notefile.contents_from_file(os.path.join(gc.NOTE_DIR, note))
                    notefile.save()
                    gc.success('Added note ' + note + '.')
                    file.write('NOTE ' + note + '\n')

            # add email folder if necessary
            if len(emails) > 0:
                gc.msg('Adding emails...')
                email_dir = Directory('emails', c.root_dir.id)
                email_dir.comp_id = c.id
                email_dir.read_only = True
                email_dir.save()
                gc.success('Added directory ' + email_dir.name + '.')
                email_dir.lookup()

                # add emails to folder
                for email in emails:
                    emailfile = File(email, email_dir)
                    emailfile.contents_from_file(os.path.join(gc.NOTE_DIR, email))
                    emailfile.type = 'email'
                    emailfile.save()
                    gc.success('Added email ' + email + '.')
                    file.write('NOTE ' + email + '\n')

            # add program folder if necessary
            if len(programs) > 0:
                gc.msg('Adding programs...')
                bin_dir = Directory('bin', c.root_dir.id)
                bin_dir.comp_id = c.id
                bin_dir.read_only = True
                bin_dir.save()
                gc.success('Added directory ' + bin_dir.name + '.')
                bin_dir.lookup()

                # add programs to folder
                for fname in programs:
                    binfile = File(fname, bin_dir)
                    binfile.program_from_file(os.path.join(gc.PROGRAM_DIR, fname))
                    binfile.save()
                    gc.success('Added binary file ' + fname + '.')
                    file.write('PROGRAM ' + fname + '\n')

            file.close()

        except Exception as e:
            gc.error('An error occurred: ' + str(e))
    else:
        gc.warning('NPC not saved.')

# Displays a list of NPCs
def show_computers(npcs_only = False):
    db = Database()
    sql = 'SELECT * FROM computers'
    if npcs_only:
        sql += ' WHERE owner_id = 0'
    results = db.get_query(sql)

    mb = MessageBox()
    if npcs_only:
        mb.set_title('List of NPCs')
    else:
        mb.set_title('List of Computers')
    for result in results:
        mb.add_property('ID ' + str(result[0]), result[1])
    mb.display()
    db.close()

# Displays a list of users
def show_users():
    db = Database()
    sql = 'SELECT * FROM users'
    results = db.get_query(sql)
    mb = MessageBox()
    mb.set_title('List of Users')
    for result in results:
        mb.add_property('ID ' + str(result[0]), result[1])
    mb.display()
    db.close()

# Shows stats about a single computer
def show_computer(c):
    mb = MessageBox()
    mb.set_title('Computer Info for ' + c.ip + ' (ID ' + str(c.id) + ')')
    mb.add_property('Password', c.password)
    mb.add_property('Owner ID', str(c.owner_id))
    if c.domain != None:
        mb.add_property('Domain', c.domain)
    mb.add_property('Last Login', c.last_login)
    if c.bank_id != None:
        mb.add_property('Bank ID', c.bank_id)
    mb.add_property('RAM', str(c.ram) + ' MB')
    mb.add_property('CPU', str(c.cpu) + ' MHz')
    mb.add_property('HDD', str(c.hdd) + ' GB')
    mb.add_property('Disk Free', gc.hr_bytes(c.disk_free))
    mb.add_property('FW Level', str(c.fw_level))
    mb.add_property('AV Level', str(c.av_level))
    mb.add_property('CR Level', str(c.cr_level))
    mb.display()

# Shows stats about a single user
def show_user(user):
    mb = MessageBox()
    mb.set_title('User info for ' + user.name + ' (ID ' + str(user.id) + ')')
    mb.add_property('Email', user.email)
    mb.add_property('Last Login', user.last_login)
    mb.add_property('Created On', user.creation_date)
    mb.add_property('Handle', user.handle)
    mb.add_property('Computer ID', str(user.computer.id))
    mb.display()

# Shows information and contents about a specific computer disk
def show_disk(computer):
    computer.print_disk_info()
    computer.print_all_contents()

# Loads NPCs from backup files into database
def load_npcs():
    npc_files = [f for f in os.listdir(gc.NPC_DIR) if os.path.isfile(os.path.join(gc.NPC_DIR, f))]
    gc.msg('NPC files found: ' + str(len(npc_files)))
    num_added = 0
    for filename in npc_files:
        # check if NPC is already in database
        db = Database()
        sql = 'SELECT * FROM computers WHERE ip = %s'
        args = [filename[:-4]]
        result = db.get_query(sql, args)
        db.close()

        if len(result) == 0:
            # add the NPC
            num_added += 1
            gc.msg('Adding NPC ' + args[0])
            try:
                file = open(os.path.join(gc.NPC_DIR, filename), 'r')
                npc = Computer(0)
                notes = []
                emails = []
                programs = []
                for line in file.readlines():
                    text = line.split()
                    if text[0] == 'IP':
                        npc.ip = text[1]
                    elif text[0] == 'PASSWORD':
                        npc.password = text[1]
                    elif text[0] == 'DOMAIN':
                        npc.domain = text[1]
                    elif text[0] == 'BANK_ID':
                        npc.domain = int(text[1])
                    elif text[0] == 'RAM':
                        npc.ram = int(text[1])
                    elif text[0] == 'CPU':
                        npc.cpu = int(text[1])
                    elif text[0] == 'HDD':
                        npc.hdd = int(text[1])
                    elif text[0] == 'FW_LEVEL':
                        npc.fw_level = int(text[1])
                    elif text[0] == 'AV_LEVEL':
                        npc.av_level = int(text[1])
                    elif text[0] == 'CR_LEVEL':
                        npc.cr_level = int(text[1])
                    elif text[0] == 'ONLINE':
                        npc.online = bool(text[1])
                    elif text[0] == 'NOTE':
                        if text[1][6:] == '.email':
                            emails.append(text[1])
                        else:
                            notes.append(text[1])
                    elif text[0] == 'PROGRAM':
                        programs.append(text[1])
                    else:
                        gc.warning('Skipping line: ' + line)
                npc.save()

                # add notes if necessary
                if len(notes) > 0:
                    npc.lookup()
                    gc.msg('Adding notes directory')
                    note_dir = Directory('notes', npc.root_dir.id)
                    note_dir.comp_id = npc.id
                    note_dir.read_only = True
                    note_dir.save()
                    note_dir.lookup()

                    for note in notes:
                        notefile = File(note, note_dir)
                        notefile.contents_from_file(os.path.join(gc.NOTE_DIR, note))
                        notefile.save()
                        gc.success('Added note ' + note + '.')

                # add emails if necessary
                if len(emails) > 0:
                    npc.lookup()
                    gc.msg('Adding email directory')
                    email_dir = Directory('emails', npc.root_dir.id)
                    email_dir.comp_id = npc.id
                    email_dir.read_only = True
                    email_dir.save()
                    email_dir.lookup()

                    for email in emails:
                        emailfile = File(email, email_dir)
                        emailfile.contents_from_file(os.path.join(gc.NOTE_DIR, email))
                        emailfile.type = 'email'
                        emailfile.save()
                        gc.success('Added email ' + email + '.')

                # add programs if necessary
                if len(programs) > 0:
                    npc.lookup()
                    gc.msg('Adding program directory')
                    bin_dir = Directory('bin', npc.root_dir.id)
                    bin_dir.comp_id = npc.id
                    bin_dir.read_only = True
                    bin_dir.save()
                    bin_dir.lookup()

                    for program in programs:
                        binfile = File(program, bin_dir)
                        binfile.program_from_file(os.path.join(gc.NOTE_DIR, program))
                        binfile.save()
                        gc.success('Added program ' + program + '.')

            except Exception as e:
                gc.error('An error occurred while reading ' + filename + '; skipping.')
                gc.error('Details: ' + str(e))

    gc.msg('NPCs added: ' + str(num_added))

if __name__ == '__main__':
    main()