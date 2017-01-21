from File import File
from Database import Database

class Directory:

    def __init__(self, username, name = '~', parent_name = ''):
        self.username = username
        self.name = name
        self.parent_name = parent_name
        self.parent_id = 0
        self.files = []
        self.subdirs = []
        self.comp_id = 0
        self.id = 0
        self.exists = False

    # gets information from database about this directory if it exists
    def lookup(self):
        db = Database()

        # get user's computer ID
        sql = 'SELECT computers.id FROM computers INNER JOIN users '
        sql += 'ON users.computer_id = computers.id WHERE username = %s'
        args = [self.username]
        self.comp_id = int(db.get_query(sql, args)[0][0])

        # get id of parent directory
        sql = 'SELECT id FROM directories WHERE dir_name = %s'
        if self.parent_name == '':
            self.parent_id = 0 # no parent if this is the root folder
        else:
            args = [self.parent_name]
            self.parent_id = int(db.get_query(sql, args)[0][0])

        # check if directory exists
        sql = 'SELECT id FROM directories WHERE dir_name = %s AND computer_id = %s '
        sql += 'AND parent_id = %s'
        args = [self.name, self.comp_id, self.parent_id]
        result = db.get_query(sql, args)

        if len(result) > 0: # directory exists
            self.exists = True
            # get directory ID
            self.id = int(db.get_query(sql, args)[0][0])

            # get files in this directory
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
            sql = 'SELECT * FROM directories WHERE parent_id = %s'
            args = [self.id]
            response = db.get_query(sql, args)
            i = 0
            while i < len(response):
                row = response[i]
                name = row[1]
                directory = Directory(self.username, name, self.name)
                self.subdirs.append(directory)
                i += 1

        db.close()

    # synchronize object with database
    def save(self):
        db = Database()
        self.lookup()
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

    # returns files and subdirectories in this directory
    def get_contents(self):
        pass

    # permanently delete this directory
    def delete(self):
        pass