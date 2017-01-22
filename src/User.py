import time

import GameController as gc

from Database import Database
from Computer import Computer

from datetime import datetime

class User:

    def __init__(self, username = '', email = '', password = '', handle = ''):
        self.name = username
        self.email = email
        self.password = password
        self.handle = handle
        self.exists = False
        self.last_login = gc.current_time()
        self.creation_date = gc.current_time()
        self.computer = Computer()
        self.id = -1

    # gets information from database for a specific username if it exists
    def lookup(self):
        db = Database()
        sql = ''
        args = []
        # search by username
        if self.name != '':
            sql = "SELECT * FROM users WHERE username = %s"
            args = [self.name]
        result = db.get_query(sql, args)
        computer_id = -1
        if len(result) > 0:
            self.exists = True
            self.id = int(result[0][0])
            self.email = result[0][2]
            self.last_login = gc.ts_to_string(result[0][3])
            self.creation_date = gc.ts_to_string(result[0][4])
            self.password = result[0][5]
            self.handle = result[0][6]
            computer_id = int(result[0][7])

        # get user's computer object
        self.computer.owner_id = self.id
        self.computer.lookup()

        db.close()

    # writes the current object's state to the database
    def save(self):
        db = Database()

        if not self.exists:
            sql = 'INSERT INTO users (username, email, last_login, creation_date, '
            sql += 'password, handle, computer_id) VALUES '
            sql += '(%s, %s, %s, %s, %s, %s, %s)'
            args = [self.name, self.email, self.last_login, self.creation_date,
                self.password, self.handle, self.computer_id]
            self.exists = True
        else:
            sql = 'UPDATE users SET email = %s, last_login = %s, '
            sql += 'creation_date = %s, password = %s, handle = %s, computer_id = %s '
            sql += 'WHERE username = %s'
            args = [self.email, self.last_login, self.creation_date,
                self.password, self.handle, self.computer_id, self.name]
        db.post_query(sql, args)
        db.close()