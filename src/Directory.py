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

# File: Directory.py
# A Directory represents a virtual in-game filesystem directory on a computer.

import GameController as gc

from File import File
from Database import Database
from MessageBox import MessageBox

from termcolor import colored

class Directory:

    def __init__(self, name = '', parent_id = -1, id = -1):
        self.name = name
        self.parent_id = parent_id
        self.files = []
        self.subdirs = []
        self.id = id
        self.comp_id = -1
        self.exists = False
        self.fullpath = '~'
        self.nesting = 0
        self.size = 0
        self.creation_time = gc.current_time()
        self.modified_time = self.creation_time
        self.read_only = False

    # gets information from database about this directory if it exists
    def lookup(self):
        db = Database()
        sql = ''
        args = []
        can_lookup = False # whether there is enough info to query the database

        # search by directory ID
        if self.id != -1:
            sql = 'SELECT * FROM directories WHERE id = %s'
            args = [self.id]
            can_lookup = True
        # search by name and parent ID
        elif self.parent_id != -1 and self.name != '':
            sql = 'SELECT * FROM directories WHERE parent_id = %s AND dir_name = %s'
            args = [self.parent_id, self.name]
            can_lookup = True

        # perform the lookup if the object has enough information
        if can_lookup:
            result = db.get_query(sql, args)
            if len(result) > 0:
                self.exists = True
                self.id = int(result[0][0])
                self.name = result[0][1]
                self.parent_id = int(result[0][2])
                self.comp_id = int(result[0][3])
                self.creation_time = gc.ts_to_string(result[0][4])
                self.modified_time = gc.ts_to_string(result[0][5])
                self.read_only = bool(result[0][6])

                # get parent's name
                sql = 'SELECT * FROM directories WHERE id = %s'
                args = [self.parent_id]
                result = db.get_query(sql, args)
                if len(result) > 0:
                    self.parent_name = result[0][1]

                # get full path of this directory
                pid = self.parent_id
                self.fullpath = self.name
                self.nesting = 1
                while pid != 0:
                    sql = 'SELECT * FROM directories WHERE id = %s'
                    args = [pid]
                    result = db.get_query(sql, args)
                    if len(result) > 0:
                        pid = int(result[0][2])
                        self.fullpath = result[0][1] + '/' + self.fullpath
                        self.nesting += 1
                    else:
                        pid = 0
                        self.fullpath = '~/' + self.fullpath

                self.size = gc.DIR_SIZE # start counting total size

                # get files in this directory
                self.files = []
                sql = 'SELECT file_name FROM files WHERE parent_id = %s'
                args = [self.id]
                response = db.get_query(sql, args)
                i = 0
                while i < len(response):
                    row = response[i]
                    name = row[0]

                    file = File(name, self)
                    file.lookup()
                    self.files.append(file)
                    self.size += file.size
                    i += 1

                # get subdirectories
                self.subdirs = []
                sql = 'SELECT * FROM directories WHERE parent_id = %s'
                args = [self.id]
                response = db.get_query(sql, args)
                for subdir in response:
                    dir_name = subdir[1]
                    d = Directory(name = dir_name, parent_id = self.id)
                    d.lookup()
                    self.subdirs.append(d)
                    self.size += d.size
                    i += 1

        db.close()

    # synchronize object with database
    def save(self):
        db = Database()
        if not self.exists:
            sql = 'INSERT INTO directories (dir_name, parent_id, computer_id, modified_time, read_only) '
            sql += 'VALUES (%s, %s, %s, %s, %s)'
            args = [self.name, self.parent_id, self.comp_id, self.modified_time, self.read_only]
            db.post_query(sql, args)
            self.exists = True
        else:
            sql = 'UPDATE directories SET dir_name = %s, parent_id = %s, computer_id = %s, '
            sql += 'modified_time = %s, read_only = %s WHERE id = %s'
            args = [self.name, self.parent_id, self.comp_id, self.id, self.modified_time, self.read_only]
            db.post_query(sql, args)

        db.close()

    # get id of this directory
    def get_id(self):
        return self.id

    # returns total size of directory
    def get_size(self):
        pass

    # returns subdirectories in this directory
    def get_subdirs(self):
        subdir_list = ''
        for subdir in self.subdirs:
            subdir_list += subdir.name + ' '
        return subdir_list

    # returns files in this directory
    def get_files(self):
        file_list = ''
        for file in self.files:
            if file.type == 'bin':
                file_list += colored(file.name, 'green') + ' '
            else:
                file_list += file.name + ' '
        return file_list

    # prints list of files and subdirectories to screen
    def print_contents(self):
        self.lookup()
        dir_list = self.get_subdirs()
        file_list = self.get_files()

        gc.msg_pair('Directories: ', colored(dir_list, 'yellow'))
        gc.msg_pair('Files:       ', file_list)

    # prints the entire file structure in this directory
    def print_all_contents(self):
        indents = u'\u251c'
        spaces = ''
        i = 1
        while i < self.nesting:
            indents += u'\u2500'
            spaces += ' '
            i += 1

        gc.msg(indents + '[' + self.name + ']')
        gc.msg(u'\u2502' + spaces + ' D: ' + colored(self.get_subdirs(), 'yellow'))
        gc.msg(u'\u2502' + spaces + ' F: ' + colored(self.get_files(), 'white'))
        for subdir in self.subdirs:
            subdir.print_all_contents()

    # permanently delete this directory and its contents
    def delete(self):
        self.lookup()
        # delete subdirectories
        for subdir in self.subdirs:
            subdir.lookup()
            subdir.delete()

        # delete files in directory
        for file in self.files:
            file.delete()

        db = Database()

        # delete self
        sql = 'DELETE FROM directories WHERE id = %s'
        args = [self.id]
        db.post_query(sql, args)

        db.close()

    # shows general information about a directory
    def print_info(self):
        self.lookup()
        mb = MessageBox()
        mb.title = self.name + ' [' + str(self.size) + ' bytes]'
        mb.add_property('Total Size', gc.hr_bytes(self.size))
        mb.add_property('Full Path', self.fullpath)
        mb.add_property('Files', self.get_files())
        mb.add_property('Subdirectories', self.get_subdirs())
        mb.add_property('Created On', self.creation_time)
        mb.add_property('Modified On', self.modified_time)
        mb.add_property('Read Only', str(self.read_only))
        mb.display()
