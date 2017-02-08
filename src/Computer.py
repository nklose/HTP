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

# File: Computer.py
# A Computer represents a virtual workstation (if owned by a User)
# or a virtual server (if owned by the game itself).
# Some Computers may be running their own web or bank servers.
# Each Computer has at least:
# - a set of hardware which determines its performance
# - an IP address that allows it to connect to the network
# - a randomly-generated root password which can be hacked by other Users
# - a root directory with a file system which may contain other files and directories
# - a log file which records any major events on the computer

import os

import GameController as gc

from File import File
from Database import Database
from Directory import Directory
from MessageBox import MessageBox

from termcolor import colored

class Computer:

    def __init__(self, owner_id = -1, id = -1):
        self.owner_id = owner_id
        self.ram = 512
        self.cpu = 512
        self.hdd = 1
        self.disk_free = self.hdd * 1024 ** 3
        self.firewall = File('none', Directory())
        self.firewall.level = 0
        self.ip = '0.0.0.0'
        self.password = ''
        self.bank_id = None
        self.domain = None
        self.id = id
        self.last_login = gc.current_time()
        self.folder_count = 0
        self.file_count = 0
        self.root_dir = Directory()    # root directory for this computer (i.e. '~')
        self.exists = False
        self.online = True

    # gets information from database for a specific computer IP if it exists
    def lookup(self):
        db = Database()
        sql = ''
        args = []
        # search by IP
        if self.ip != '0.0.0.0':
            sql = 'SELECT * FROM computers WHERE ip = %s'
            args = [self.ip]
        # search by domain
        elif self.domain != None:
            sql = 'SELECT * FROM computers WHERE domain_name = %s'
            args = [self.domain]
        # search by ID
        elif self.id != -1:
            sql = 'SELECT * FROM computers WHERE id = %s'
            args = [self.id]
        # search by owner's ID
        elif self.owner_id != -1:
            sql = 'SELECT * FROM computers WHERE owner_id = %s'
            args = [self.owner_id]
        result = db.get_query(sql, args)
        if len(result) > 0:
            self.exists = True
            self.id = int(result[0][0])
            self.ip = result[0][1]
            self.password = result[0][2]
            self.domain = result[0][3]
            self.owner_id = int(result[0][4])
            self.last_login = gc.ts_to_string(result[0][5])
            if result[0][6] != None:
                self.bank_id = int(result[0][6])
            else:
                self.bank_id = None
            self.ram = int(result[0][7])
            self.cpu = int(result[0][8])
            self.hdd = int(result[0][9])
            self.online = bool(result[0][10])
            self.check_space()

            # get root folder ID
            sql = 'SELECT * FROM directories WHERE parent_id = %s AND computer_id = %s'
            args = [0, self.id]
            result = db.get_query(sql, args)
            if len(result) > 0:
                self.root_dir.id = int(result[0][0])
                self.root_dir.lookup()
        db.close()

        # select the appropriate firewall
        self.set_firewall()

    # writes the current object's state to the database
    def save(self):
        db = Database()

        sql = ''

        if not self.exists:
            # create the computer
            sql = 'INSERT INTO computers (ip, password, domain_name, owner_id, last_login, bank_id, '
            sql += 'ram, cpu, hdd, online) VALUES '
            sql += '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            args = [self.ip, self.password, self.domain, self.owner_id, self.last_login,
                self.bank_id, self.ram, self.cpu, self.hdd, self.online]
            self.exists = True
            db.post_query(sql, args)
            self.lookup()

            # create a home directory for the computer
            sql = 'INSERT INTO directories (dir_name, parent_id, computer_id) VALUES (%s, %s, %s)'
            args = ['~', 0, self.id]
            db.post_query(sql, args)
        else:
            sql = 'UPDATE computers SET password = %s, owner_id = %s, last_login = %s, '
            sql += 'bank_id = %s, ram = %s, cpu = %s, hdd = %s, online = %s '
            sql += 'WHERE ip = %s'
            args = [self.password, self.domain, self.owner_id, self.last_login, self.bank_id,
                self.ram, self.cpu, self.hdd, self.online, self.ip]
            db.post_query(sql, args)
        db.close()

    # check how much disk space is free
    def check_space(self):
        db = Database()

        # get a list of all directories
        total_bytes = 0
        self.folder_count = 0
        self.file_count = 0
        sql = 'SELECT * FROM directories WHERE computer_id = %s'
        args = [self.id]
        result = db.get_query(sql, args)
        if result != None:
            for d in result:
                dir_id = d[0]
                total_bytes += gc.DIR_SIZE # the directory itself takes up some space
                self.folder_count += 1
                sql = 'SELECT * FROM files WHERE parent_id = %s'
                args = [dir_id]
                f_result = db.get_query(sql, args)
                for file in f_result:
                    self.file_count += 1
                    f_size = 0
                    f_type = file[4]
                    if f_type == 'txt': # for text files, size is length of name and content
                        f_size = len(file[1])
                        if file[3] != None:
                            f_size += len(file[3])
                    else:
                        f_size = int(file[6])

                    total_bytes += f_size
            self.disk_free = self.hdd * 1024 ** 3 - int(total_bytes)

        db.close()

    # shows information about this computer's disk
    def print_disk_info(self):
        self.check_space()
        mb = MessageBox()
        mb.set_title('Disk Info')
        mb.add_property('Total Folders', str(self.folder_count))
        mb.add_property('Total Files', str(self.file_count))
        mb.add_property('Disk Size', str(self.hdd) + ' GB')
        mb.add_property('Free Space', gc.hr_bytes(self.disk_free))
        mb.add_property('Free Space (B)', gc.hr_large(self.disk_free) + ' B')
        mb.display()

    # shows all of a computer's disk contents
    def print_all_contents(self):
        self.root_dir.print_all_contents()


    # prints the log file for this computer
    def print_log_file(self):
        osdir = Directory('os', self.root_dir.id)
        osdir.lookup()
        logfile = File('log.txt', osdir)
        logfile.lookup()
        logfile.print_contents()

    # adds an entry to the log, and creates it if it doesn't already exist
    def add_log_entry(self, text):
        db = Database()

        # check for the folder ~/os
        sql = 'SELECT * FROM directories WHERE dir_name = %s AND computer_id = %s '
        sql += 'AND parent_id = %s'
        args = ['os', self.id, self.root_dir.id]
        result = db.get_query(sql, args)
        if len(result) == 0:
            # create the system directory
            sql = 'INSERT INTO directories (dir_name, parent_id, computer_id) VALUES '
            sql += '(%s, %s, %s)'
            args = ['os', self.root_dir.id, self.id]
            db.post_query(sql, args)

        # get the system directory's ID
        sql = 'SELECT * FROM directories WHERE dir_name = %s AND computer_id = %s '
        sql += 'AND parent_id = %s'
        args = ['os', self.id, self.root_dir.id]
        sys_dir_id = int(db.get_query(sql, args)[0][0])

        # check for logfile
        sql = 'SELECT * FROM files WHERE file_name = %s AND parent_id = %s'
        args = ['log.txt', sys_dir_id]
        result = db.get_query(sql, args)
        if len(result) == 0:
            # create the logfile
            sql = 'INSERT INTO files (file_name, parent_id, content, file_type, file_level, file_size) '
            sql += 'VALUES (%s, %s, %s, %s, %s, %s)'
            create_entry = '[' + gc.current_time() + '] LOG FILE CREATED\n'
            args = ['log.txt', sys_dir_id, create_entry, 'txt', 1, len(create_entry)]
            db.post_query(sql, args)

        # get the ID of the logfile
        sql = 'SELECT * FROM files WHERE file_name = %s AND parent_id = %s'
        args = ['log.txt', sys_dir_id]
        log_id = int(db.get_query(sql, args)[0][0])
        log_content = db.get_query(sql, args)[0][3]

        # finally, add text to the logfile
        log_entry = '[' + gc.current_time() + '] ' + text + '\n'
        new_content = log_content + log_entry
        while len(new_content) > gc.MAX_FILE_SIZE: # remove lines top as needed
            nl_index = new_content.index('\n') + 1 # find first newline character
            new_content = new_content[nl_index:]   # remove text up to first newline
        sql = 'UPDATE files SET content = %s, modified_time = now() WHERE id = %s'
        args = [new_content, log_id]
        db.post_query(sql, args)
        db.close()

    # adds a default set of files for new users
    def add_default_files(self):
        self.root_dir.lookup()
        if self.root_dir.exists:
            # add initial note
            note = File('note.txt', self.root_dir)
            note.load_note('note.txt')
            note.save()

            # add basic firewall
            fname = 'fw-free-v1.bin'
            fw = File(fname, self.root_dir)
            fw.program_from_file(os.path.join(gc.PROGRAM_DIR, fname))
            fw.save()
            self.firewall = fw

            # update storage info
            self.check_space()

        else:
            gc.error('An error occurred while creating the default files.')

    # get os directory for this computer
    def get_os_dir(self):
        db = Database()
        sql = 'SELECT * FROM directories WHERE parent_id = %s AND dir_name = %s'
        args = [self.root_dir.id, 'os']
        result = db.get_query(sql, args)
        db.close()
        if len(result) > 0:
            os_dir = Directory(id = result[0][0])
            os_dir.lookup()
            if os_dir.exists:
                return os_dir
            else:
                gc.error('An invalid OS directory ID was specified.')
        else:
            # create the OS directory
            os_dir = Directory('os', self.root_dir.id)
            os_dir.comp_id = self.id
            os_dir.save()
            os_dir.lookup()
            return os_dir

    # show login banner text
    def show_login_banner(self):
        banner_file = File('banner.txt', self.get_os_dir())
        banner_file.lookup()
        if not banner_file.exists:
            banner_file.content = 'Welcome to ' + self.ip + '.'
            banner_file.save()
        banner_lines = banner_file.content.split('\n')
        lines_printed = 0
        for line in banner_lines:
            if lines_printed < 10:
                print '    ' + colored(line, 'yellow')
            lines_printed += 1

    # return a list of all files on this computer
    def get_all_files(self):
        all_files = []
        all_dirs = [self.root_dir] + self.root_dir.subdirs
        for directory in all_dirs:
            all_files += directory.files
        return all_files

    # select which firewall to use
    def set_firewall(self):
        for file in self.get_all_files():
            # check if file is a firewall
            if file.category == 'FIREWALL' and file.level > self.firewall.level:
                # check if there is enough memory to run it
                if file.memory <= self.get_memory_free():
                    # set this as the new firewall
                    self.firewall = file


    # calculates how much memory is available for new processes
    def get_memory_free(self):
        free = self.ram
        # check OS memory
        free -= gc.OS_MEMORY
        # check memory used by firewall
        if self.firewall.memory != None:
            free -= self.firewall.memory
        # add process memory
        db = Database()
        sql = 'SELECT * FROM processes WHERE user_id = %s'
        args = [self.owner_id]
        results = db.get_query(sql, args)
        for result in results:
            free -= int(result[6])
        db.close()
        return free