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

# File: Database.py
# A User represents a single player account in the game.
# In the game, a User is known by their handle (which can be changed).
# Usernames, emails, and passwords are only used for registration and login.

import os
import re
import time
import smtplib
import yagmail

import GameController as gc

from Database import Database
from Computer import Computer
from MessageBox import MessageBox
from Directory import Directory

from datetime import datetime
from getpass import getpass

class User:

    def __init__(self, username = '', email = '', password = '', handle = ''):
        self.name = username
        self.email = email
        self.email_confirmed = False
        self.password = password
        self.handle = handle
        self.exists = False
        self.last_login = gc.current_time()
        self.creation_date = gc.current_time()
        self.computer = Computer()
        self.id = -1
        self.token = ''
        self.token_date = None

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
            email_confirmed = int(result[0][3])
            self.email_confirmed = email_confirmed == 1
            self.last_login = gc.ts_to_string(result[0][4])
            self.creation_date = gc.ts_to_string(result[0][5])
            self.password = result[0][6]
            self.handle = result[0][7]
            computer_id = int(result[0][8])
            self.token = result[0][9]
            self.token_date = result[0][10]

            # get user's computer object
            self.computer.owner_id = self.id
            self.computer.lookup()

        db.close()

    # writes the current object's state to the database
    def save(self):
        db = Database()

        if not self.exists:
            sql = 'INSERT INTO users (username, email, email_confirmed, last_login, creation_date, '
            sql += 'password, handle, computer_id, token, token_date) VALUES '
            sql += '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            args = [self.name, self.email, self.email_confirmed, self.last_login, self.creation_date,
                self.password, self.handle, self.computer.id, self.token, self.token_date]
            self.exists = True
        else:
            sql = 'UPDATE users SET email = %s, email_confirmed = %s, last_login = %s, '
            sql += 'creation_date = %s, password = %s, handle = %s, computer_id = %s, '
            sql += 'token = %s, token_date = %s WHERE username = %s'
            args = [self.email, self.email_confirmed, self.last_login, self.creation_date,
                self.password, self.handle, self.computer.id, self.token,
                self.token_date, self.name]
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
        msg_box.add_property('Free', gc.hr_bytes(c.disk_free))
        msg_box.add_property('Firewall', 'Level ' + str(c.fw_level))
        msg_box.add_property('Antivirus', 'Level ' + str(c.av_level))
        msg_box.hr()
        msg_box.add_property('IP Address', c.ip)
        msg_box.add_property('Root Password', str(c.password))
        msg_box.hr()
        # add user details
        msg_box.add_property('Handle', self.handle)
        msg_box.add_property('Last Login', str(self.last_login) + ' [MST]')
        # number of bank accounts
        msg_box.add_property('Total Funds', str(total_funds) + ' dollars')
        msg_box.add_property('# of Accounts', str(num_accounts))

        msg_box.display()
        os_msg = 'You are running YardleOS ' + str(gc.GAME_VERSION) + ' (last updated '
        os_msg += gc.GAME_TIMESTAMP + ')\n'
        gc.msg(os_msg)

        c.show_login_banner()

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
        gc.hr()

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

        gc.hr()

        # get a valid password
        gc.msg('You can now set a password for your account.')
        valid_password = False
        while not valid_password:
            password = getpass()
            if len(password) < 6:
                gc.error('Your password must contain 6 or more characters.')
            else:
                confirm = getpass('Confirm: ')
                if password != confirm:
                    gc.error('Sorry, those passwords didn\'t match.')
                else:
                    valid_password = True
                    self.password = gc.hash_password(password, self.name)

        gc.hr()

        # get a valid email address (optional for users)
        email_set = False
        gc.msg('You may optionally enter an email address which will enable password resets.')
        gc.msg('If you leave this blank, you will not be able to recover your account if you forget your password.')
        while not email_set:
            self.email = raw_input('Email Address: ')
            if self.email == '':
                gc.warning('You have opted not to attach an email address to your account.')
                email_set = True
            elif re.match(r'[^@]+@[^@]+\.[^@]+', self.email):
                # check if email exists in database
                sql = 'SELECT * FROM users WHERE email = %s;'
                response = db.get_query(sql, [self.email])
                if len(response) > 0:
                    gc.error('Sorry, that email has already been registered.')
                else:
                    email_set = True
            else:
                gc.error('Sorry, your input was not in the right format for an email address.')

        gc.hr()

        # get a unique in-game handle
        gc.msg('Finally, you need to choose an in-game handle that others can see.')
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

        gc.hr()

        # send a confirmation email to the user if necessary
        self.confirm_email()

        # generate an IP address for the user
        self.computer.ip = gc.gen_ip()

        self.save()     # write user to database
        self.lookup()   # get generated id for the user

        # update computer information
        self.computer.password = gc.gen_password()
        self.computer.owner_id = self.id

        self.computer.save()     # write computer to database
        self.computer.lookup()   # get generated id for computer

        self.save()

        # generate default directories and files
        self.computer.add_default_files()

        gc.success('Account ' + self.name + ' created!')

        # close database
        db.close()

    # sends a confirmation email to validate the user's email address
    def confirm_email(self):
        if self.email != '':
            try:
                emailuser = os.environ['emailuser']
                emailpass = os.environ['emailpass']
                yag = yagmail.SMTP(emailuser, emailpass)
                self.token = gc.gen_token()
                self.token_date = gc.current_time()
                subject = 'HTP Email Confirmation'
                msg = 'Greetings!\n\n'
                msg += 'Your email address has been listed for an account on HTP with username '
                msg += '<b>' + self.name + '</b>.\n\n'
                msg += '<b>If you didn\'t request this:</b>'
                msg += '<ul><li>Disregard this email.</li>'
                msg += '<li>If you keep getting these messages, please reply and tell us.</li></ul>'
                msg += '<b>If you are confirming your email address:</b>\n'
                msg += '<ul><li>Log into the game</li>'
                msg += '<li>Enter the command <b>verify ' + self.token + '</b></li></ul>'
                msg += '<b>If you have forgotten your password:</b>'
                msg += '<ul><li>Start the game client</li>'
                msg += '<li>Choose the \'Reset Password\' option</li>'
                msg += '<li>Enter your username (<b>' + self.name + '</b>)</li>'
                msg += '<li>Enter the token <b>' + self.token + '</b></li></ul>'
                msg += 'Sincerely,\nHTP Staff'
                yag.send(self.email, subject, msg)
                gc.success('Confirmation email sent.')
            except KeyError as e:
                gc.error('A problem occurred while sending the confirmation email.')

    # update last login time on user login
    def new_login(self):
        self.last_login = gc.current_time()
        self.save()
        log_entry = 'new session for ' + self.handle + ' [' + self.computer.ip + ']'
        self.computer.add_log_entry(log_entry)

    # returns the home directory of the user
    def get_home_dir(self):
        db = Database()
        sql = 'SELECT * FROM directories WHERE computer_id = %s AND dir_name = %s'
        args = [self.computer.id, '~']
        result = db.get_query(sql, args)
        home_dir_id = int(result[0][0])
        home_dir = Directory(id = home_dir_id)
        home_dir.lookup()
        return home_dir

