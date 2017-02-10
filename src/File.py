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

# File: File.py
# A File represents a virtual in-game file on a computer.

import os

import GameController as gc

from Database import Database
from MessageBox import MessageBox

from termcolor import colored

class File:

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.owner_id = -1
        self.id = -1
        self.content = None
        self.type = 'txt'
        self.level = 1
        self.size = 0
        self.exists = False
        self.creation_time = gc.current_time()
        self.modified_time = self.creation_time
        self.category = None
        self.comment = None
        self.memory = None
        self.is_live = False

        if type == 'txt':
            self.size = len(content)

    # gets information from database about this file if it exists
    def lookup(self):
        db = Database()
        sql = 'SELECT * FROM files WHERE file_name = %s AND parent_id = %s'
        args = [self.name, self.parent.id]
        result = db.get_query(sql, args)
        db.close()
        if len(result) == 1: # file exists
            self.exists = True
            self.id = int(result[0][0])
            self.owner_id = int(result[0][3])
            self.content = result[0][4]
            self.type = result[0][5]
            self.level = int(result[0][6])
            self.size = int(result[0][7])
            self.creation_time = gc.ts_to_string(result[0][8])
            self.modified_time = gc.ts_to_string(result[0][9])
            self.category = result[0][10]
            self.comment = result[0][11]
            if result[0][12] != None:
                self.memory = int(result[0][12])
            self.is_live = bool(result[0][13])
            if self.type == 'txt':
                self.size = len(self.name)
                if self.content != None:
                    self.size += len(self.content)

    # synchronize object with database
    def save(self):
        db = Database()

        # update file size
        if self.type == 'txt':
            self.size = len(self.name)
            if self.content != None:
                self.size += len(self.content)

        # update modified timestamp
        self.modified_time = gc.current_time()

        args = [self.name, self.parent.id, self.owner_id, self.content, self.type,
                self.level, self.size, self.category, self.comment, self.memory, self.is_live]

        self.lookup()
        if not self.exists:
            sql = 'INSERT INTO files (file_name, parent_id, owner_id, content, file_type, '
            sql += 'file_level, file_size, category, comment, memory, modified_time, is_live) '
            sql += 'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), %s)'
        else:
            sql = 'UPDATE files SET file_name = %s, parent_id = %s, owner_id = %s, content = %s, '
            sql += ' file_type = %s, file_level = %s, file_size = %s, modified_time = now(), category = %s, '
            sql += 'comment = %s, memory = %s, is_live = %s WHERE id = %s'
            args.append(self.id)
        db.post_query(sql, args)
        db.close()

    def get_content(self):
        return self.content

    def rename(self, new_name):
        pass

    def copy(self, dest_id):
        pass

    # permanently delete this file
    def delete(self):
        self.lookup()
        db = Database()
        sql = 'DELETE FROM files WHERE id = %s'
        args = [self.id]
        db.post_query(sql, args)
        db.close()

    # shows general information about a file
    def print_info(self):
        self.lookup()
        mb = MessageBox()
        mb.title = self.name + ' [' + gc.hr_large(self.size) + ' bytes]'
        mb.add_property('Total Size', gc.hr_bytes(self.size))
        mb.add_property('File Type', gc.str_to_type(self.type))
        mb.add_property('Parent Folder', self.parent.fullpath)
        if not self.is_live:
            mb.add_property('Level', str(self.level))
        mb.add_property('Created On', self.creation_time)
        mb.add_property('Modified On', self.modified_time)
        if self.category != None and self.category != '' and not self.is_live:
            mb.add_property('Category', self.category)
        if self.memory != 0:
            mb.add_property('Memory Req.', str(self.memory) + ' MB')
        if not self.is_live:
            mb.add_long_text('COMMENT: ' + self.comment)
        mb.display()

    # prints the contents of a file
    def print_contents(self):
        if len(self.content) > 0:
            # construct message box
            mb = MessageBox()
            mb.title = self.name + ' [' + str(self.size) + ' bytes]'
            for line in self.content.split('\n'):
                mb.add_long_text(line)

            # check for long file
            if self.size > gc.LONG_FILE_CUTOFF:
                gc.warning(self.name + ' is quite big (' + gc.hr_large(self.size) + ' bytes).')
                confirm = raw_input('  Open the file anyway? (Y/N): ')
                if confirm.lower() == 'y':
                    mb.display()
                else:
                    gc.warning('File not displayed.')
            else:
                mb.display()
        else:
            gc.error('The file you specified is blank; nothing to show.')

    # populates the contents from a real file on disk
    def contents_from_file(self, filepath):
        text = ''
        f = open(filepath, 'r')
        lines = f.readlines()
        for line in lines:
            text += line

        self.content = text
        self.size = len(self.content) + len(self.name)

    # creates a binary file based on a textual description from a real file on disk
    def program_from_file(self, filepath):
        self.name = os.path.basename(filepath)
        self.type = 'bin'

        text = ''
        f = open(filepath, 'r')
        lines = f.readlines()
        for line in lines:
            text = line.split()
            if len(text) > 0:
                if text[0] == 'LEVEL':
                    self.level = int(text[1])
                elif text[0] == 'SIZE':
                    self.size = int(text[1])
                elif text[0] == 'MEMORY':
                    self.memory = int(text[1])
                elif text[0] == 'CATEGORY':
                    self.category = text[1]
                elif text[0] == 'COMMENT':
                    self.comment = line[8:]
                else:
                    gc.warning('Program ' + self.name + ' has a formatting issue.')

    # loads a specific note file
    def load_note(self, name):
        filepath = os.path.join(gc.NOTE_DIR, name)
        self.contents_from_file(filepath)

    # returns True only if this file is the OS log file for its computer
    def is_log_file(self):
        return self.name == 'log.txt' and self.parent.name == 'os' and self.parent.nesting == 2
