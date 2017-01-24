from Database import Database

class File:

    def __init__(self, name, parent, content = '', type = 'txt', level = 1, size = 0):
        self.name = name
        self.parent = parent
        self.parent_id = parent.id
        self.content = content
        self.type = type
        self.level = level
        self.size = size
        self.exists = False
        self.id = -1

        if type == 'txt':
            self.size = len(content)

    # gets information from database about this file if it exists
    def lookup(self):
        db = Database()

        sql = 'SELECT * FROM files WHERE file_name = %s AND parent_id = %s'
        args = [self.name, self.parent_id]
        result = db.get_query(sql, args)

        if len(result) > 0: # file exists
            self.exists = True
            self.id = int(result[0][0])
            self.content = result[0][3]
            self.type = result[0][4]
            self.level = int(result[0][5])
            self.size = int(result[0][6])

        db.close()

    def get_content(self):
        return self.content

    def rename(self, new_name):
        pass

    def move(self, new_dir_id):
        pass

    def copy(self, dest_id):
        pass

    # synchronize object with database
    def save(self):
        db = Database()
        args = [self.name, self.parent_id, self.content, self.type,
                self.level, self.size]

        if not self.exists:
            sql = 'INSERT INTO files (file_name, parent_id, content, file_type, '
            sql += 'file_level, file_size) VALUES (%s, %s, %s, %s, %s, %s)'
        else:
            sql = 'UPDATE directories SET file_name = %s, parent_id = %s, content = %s '
            sql += ' file_type = %s, file_level = %s, file_size = %s'

        db.post_query(sql, args)
        db.close()

    # permanently delete this file
    def delete(self):
        self.lookup()
        db = Database()
        sql = 'DELETE FROM files WHERE id = %s'
        args = [self.id]
        db.post_query(sql, args)
        db.close()
