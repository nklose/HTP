import time

import GameController as gc

from Database import Database
from Computer import Computer
from MessageBox import MessageBox

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
                self.password, self.handle, self.computer.id]
            self.exists = True
        else:
            sql = 'UPDATE users SET email = %s, last_login = %s, '
            sql += 'creation_date = %s, password = %s, handle = %s, computer_id = %s '
            sql += 'WHERE username = %s'
            args = [self.email, self.last_login, self.creation_date,
                self.password, self.handle, self.computer.id, self.name]
        db.post_query(sql, args)
        db.close()

    # Displays user summary
    def show_summary(self):
        db = Database ()

        # get bank account info
        sql = 'SELECT funds FROM bank_accounts WHERE owner_id = %s'
        response = db.get_query(sql, [self.id])
        num_accounts = 0
        total_funds = 0
        if response is not None:
            num_accounts = len(response)
            i = 0
            while i < len(response):
                total_funds += int(response[i][0])
                i += 1

        # close database
        db.close()

        # display all info
        c = self.computer
        msg_box = MessageBox()
        msg_box.set_title('User Summary')
        msg_box.add_property('RAM', str(c.ram) + ' MB')
        msg_box.add_property('CPU', str(c.cpu) + ' MHz')
        msg_box.add_property('Disk', str(c.hdd) + ' GB')
        msg_box.add_property('Free', str(c.disk_free) + ' GB')
        msg_box.add_property('Firewall', 'Level ' + str(c.fw_level))
        msg_box.add_property('Antivirus', 'Level ' + str(c.av_level))
        msg_box.add_property('Cracker', 'Level ' + str(c.cr_level))
        msg_box.hr()
        msg_box.add_property('IP Address', c.ip)
        msg_box.add_property('Comp. Password', str(c.password))
        msg_box.hr()
        # add user details
        msg_box.add_property('Handle', self.handle)
        msg_box.add_property('Last Login', str(self.last_login))
        # number of bank accounts
        msg_box.add_property('Total Funds', str(total_funds) + ' dollars')
        msg_box.add_property('# of Accounts', str(num_accounts))

        msg_box.display()