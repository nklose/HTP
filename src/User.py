import re
import time

import GameController as gc

from Database import Database
from Computer import Computer
from MessageBox import MessageBox

from datetime import datetime
from getpass import getpass

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

    def login(self):
        db = Database()
        valid_creds = False
        attempts = 1
        while not valid_creds:
            username = raw_input('Username: ')
            password = getpass()

            sql = 'SELECT password FROM users WHERE username = %s'
            password_hash = db.get_query(sql, [username])

            if attempts > 4:
                gc.error('Disconnecting after 5 failed login attempts.')
                exit()
            elif len(password_hash) == 0 or not gc.check_hash(password, password_hash[0][0]):
                time.sleep(2)
                gc.error('Invalid credentials. Please try again.')
                attempts += 1
            else:
                gc.success('Credentials validated. Logging in...')
                self.name = username
                self.lookup()
                valid_creds = True

        # close database
        db.close()

    def register(self):
        gc.msg('\nStarting the account creation process...')
        gc.msg('Your username can be between 4 and 16 characters and must be alphanumeric.')
        valid_user = False
        db = Database()
        while not valid_user:
            self.name = raw_input('Desired Username: ')

            # name cannot be blank
            if self.name == '':
                gc.error('You must enter a username.')
            # name must be alphanumeric; symbols are rejected prior to database lookup
            elif not self.name.isalnum():
                gc.error('Your username can only contain letters and numbers.')
            # name must be between 4 and 16 characters
            elif len(self.name) < 4 or len(self.name) > 16:
                gc.error('Your username must be between 4 and 16 characters.')
            # name must not already exist in database
            else:
                sql = 'SELECT * FROM users WHERE username = %s;'
                response = db.get_query(sql, [self.name])
                if len(response) > 0:
                    gc.error('Sorry, that name is taken. Please choose another.')
                else:
                    gc.msg('Username is available!')
                    valid_user = True

        # get a valid password
        gc.msg('\n  You can now set a password for your account.')
        valid_password = False
        while not valid_password:
            password = getpass()
            confirm = getpass('Confirm: ')
            if len(password) < 6:
                gc.error('Your password must contain 6 or more characters.')
            elif password != confirm:
                gc.error('Sorry, those passwords didn\'t match.')
            else:
                valid_password = True
                self.password = gc.hash_password(password, self.name)

        # get a valid email address
        valid_email = False
        gc.msg('\n  You will need to enter a valid email in case you forget your password.')
        while not valid_email:
            self.email = raw_input('Email Address: ')
            if re.match(r'[^@]+@[^@]+\.[^@]+', self.email):
                # check if email exists in database
                sql = 'SELECT * FROM users WHERE email = %s;'
                response = db.get_query(sql, [self.email])
                if len(response) > 0:
                    gc.error('Sorry, that email has already been registered.')
                else:
                    valid_email = True
            else:
                gc.error('Sorry, your input was not in the right format for an email address.')

        # get a unique in-game handle
        gc.msg('\n  Finally, you need to choose an in-game handle that others can see.')
        gc.msg('This is separate from your username, and can be changed later.')
        valid_handle = False
        while not valid_handle:
            self.handle = raw_input('Please enter a handle: ')
            if self.handle == '':
                gc.error('You must enter a handle.')
            elif not self.handle.isalnum():
                gc.error('Your handle can only contain letters and numbers.')
            elif len(self.handle) < 2 or len(self.handle) > 16:
                gc.error('Your handle must be between 2 and 16 characters.')
            else:
                sql = 'SELECT * FROM users WHERE handle = %s;'
                response = db.get_query(sql, [self.handle])
                if len(response) > 0:
                    gc.error('Sorry, that handle is taken. Please choose another.')
                else:
                    valid_handle = True

        # generate an IP address for the user
        valid_ip = False
        while not valid_ip:
            self.computer.ip = gc.gen_ip()
            # check if the IP has been assigned already
            sql = 'SELECT * FROM computers WHERE ip = %s;'
            response = db.get_query(sql, [self.computer.ip])
            if len(response) == 0:
                valid_ip = True

        self.save()     # write user to database
        self.lookup()   # get generated id for the user

        # update computer information
        self.computer.password = gc.gen_password()
        self.computer.owner_id = self.id

        self.computer.save()     # write computer to database
        self.computer.lookup()   # get generated id for computer

        self.save()

        gc.success('\n Account ' + self.name + ' created!')

        # close database
        db.close()