import GameController as gc

from File import File
from Database import Database

from termcolor import colored

class Directory:

    def __init__(self, username = '', name = '', parent_id = -1, parent_name = '', comp_id = -1, id = -1):
        self.username = username
        self.name = name
        self.parent_name = parent_name
        self.parent_id = parent_id
        self.files = []
        self.subdirs = []
        self.comp_id = comp_id
        self.id = id
        self.exists = False
        self.fullpath = '~'
        self.nesting = 0

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
        # search by username and directory name (first result only)
        elif self.username != '' and self.name != '':
            # get the user's computer ID
            sql = 'SELECT computer_id FROM users WHERE username = %s'
            result = db.get_query(sql, [self.username])
            if len(result) > 0:
                self.comp_id = int(result[0][0])
                sql = 'SELECT * FROM directories WHERE computer_id = %s'
                args = [self.comp_id]
                can_lookup = True

        # perform the lookup if the object has enough information
        if can_lookup:
            result = db.get_query(sql, args)
            if len(result) > 0:
                self.exists = True
                self.id = int(result[0][0])
                self.parent_id = int(result[0][2])
                self.comp_id = int(result[0][3])

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
                    i += 1

                # get subdirectories
                self.subdirs = []
                sql = 'SELECT * FROM directories WHERE parent_id = %s'
                args = [self.id]
                response = db.get_query(sql, args)
                i = 0
                while i < len(response):
                    row = response[i]
                    name = row[1]
                    directory = Directory(self.username, name, self.name)
                    directory.lookup()
                    self.subdirs.append(directory)
                    i += 1

        db.close()

    # synchronize object with database
    def save(self):
        db = Database()
        if not self.exists:
            sql = 'INSERT INTO directories (dir_name, parent_id, computer_id) VALUES '
            sql += '(%s, %s, %s)'
            args = [self.name, self.parent_id, self.comp_id]
            db.post_query(sql, args)
            self.exists = True
        else:
            sql = 'UPDATE directories SET dir_name = %s, parent_id = %s, computer_id = %s '
            sql += 'WHERE id = %s'
            args = [self.name, self.parent_id, self.comp_id, self.id]
            db.post_query(sql, args)

        db.close()

    # get id of this directory
    def get_id(self):
        return self.id

    # returns total size of directory
    def get_size(self):
        pass

    # adds a file to the directory
    def add_file(self, file):
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
            file_list += file.name + ' '
        return file_list

    # prints contents to screen
    def print_contents(self):
        self.lookup()
        dir_list = self.get_subdirs()
        file_list = self.get_files()

        gc.msg_pair('Directories: ', colored(dir_list, 'yellow'))
        gc.msg_pair('Files:       ', file_list)

    # permanently delete this directory and its contents
    def delete(self):
        self.lookup()
        # delete subdirectories
        print self.subdirs
        for subdir in self.subdirs:
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
