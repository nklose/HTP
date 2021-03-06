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

from File import File
from Process import Process
from Database import Database
from Computer import Computer
from MessageBox import MessageBox
from Directory import Directory

from datetime import datetime
from getpass import getpass

from termcolor import colored

class User:

    def __init__(self, username = '', email = '', password = '', handle = '', id = -1):
        self.name = username
        self.email = email
        self.email_confirmed = False
        self.password = password
        self.handle = handle
        self.exists = False
        self.last_login = gc.current_time()
        self.creation_date = gc.current_time()
        self.computer = Computer()
        self.id = id
        self.token = ''
        self.token_date = None

    # gets information about user from database
    def lookup(self):
        db = Database()
        sql = ''
        args = []

        # search by username
        if self.name != '':
            sql = 'SELECT * FROM users WHERE username = %s'
            args = [self.name]
        # search by ID
        elif self.id != -1:
            sql = 'SELECT * FROM users WHERE id = %s'
            args = [self.id]
        else:
            gc.error('Not enough information to look up user.')

        # get information
        result = db.get_query(sql, args)
        computer_id = -1
        if len(result) > 0:
            self.exists = True
            self.id = int(result[0][0])
            self.name = result[0][1]
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

        # get process count
        sql = 'SELECT * FROM processes WHERE user_id = %s'
        args = [self.id]
        num_processes = len(db.get_query(sql, args))

        # close database
        db.close()

        # display all info
        c = self.computer
        c.get_memory_free()
        msg_box = MessageBox()
        msg_box.set_title('User Summary')
        # basic summary
        msg_box.add_property('CPU', str(c.cpu) + ' MHz')
        msg_box.add_property('RAM Total', str(c.ram) + ' MB')
        msg_box.add_property('RAM Free', str(c.get_memory_free()) + ' MB')
        msg_box.add_property('Disk Total', str(c.hdd) + ' GB')
        msg_box.add_property('Disk Free', gc.hr_bytes(c.disk_free))
        msg_box.add_property('Process Count', str(num_processes))
        msg_box.hr()
        # security info
        msg_box.add_property('IP Address', c.ip)
        msg_box.add_property('Firewall', 'Level ' + str(c.firewall.level) + ' (' + c.firewall.name + ')')
        msg_box.add_property('Last Login', str(self.last_login) + ' [MST]')
        msg_box.add_property('Root Password', str(c.password))
        msg_box.hr()
        # user details
        msg_box.add_property('Handle', self.handle)
        msg_box.add_property('Total Funds', str(total_funds) + ' dollars')
        msg_box.add_property('# of Accounts', str(num_accounts))

        msg_box.display()
        os_msg = 'You are running YardleOS ' + str(gc.GAME_VERSION) + ' (last updated '
        os_msg += gc.GAME_TIMESTAMP + ')\n'
        gc.msg(os_msg)

    def login(self):
        db = Database()
        valid_creds = False
        attempts = 1
        while not valid_creds:
            username = raw_input('\n\tUsername: ')
            password = getpass('\tPassword: ')

            sql = 'SELECT password FROM users WHERE username = %s'
            password_hash = db.get_query(sql, [username])

            if attempts > 4:
                gc.error('\nDisconnecting after 5 failed login attempts.')
                exit()
            elif len(password_hash) == 0 or not gc.check_hash(password, password_hash[0][0]):
                time.sleep(2)
                gc.error('\nInvalid credentials. Please try again.')
                attempts += 1
            else:
                gc.success('\nCredentials validated. Logging in...')
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
            self.name = gc.prompt('Desired Username')

            # name cannot be blank
            if self.name == '':
                gc.error('You must enter a username.')
            # name must be alphanumeric; symbols are rejected prior to database lookup
            elif not self.name.isalnum():
                gc.error('Your username can only contain letters and numbers.')
            # name must be between 4 and 16 characters
            elif len(self.name) < 4 or len(self.name) > 16:
                gc.error('Your username must be between 4 and 16 characters.')
            # first character must be a letter
            elif self.name[0].isdigit():
                gc.error('Your username must start with a letter.')
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
            self.email = gc.prompt('Email Address')
            if self.email == '':
                gc.warning('You have opted not to attach an email address to your account.')
                email_set = True
                self.email = None
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
            elif self.handle[0].isdigit():
                gc.error('Your handle must start with a letter.')
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
        if self.email != None:
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
        self.increment_stat('login_count')

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

    # attempts a password reset on an account
    def reset_password(self):
        db = Database()
        gc.msg('Beginning the password reset process...')
        self.name = gc.prompt('Please enter your username')
        self.lookup()
        # check if the user is registered
        if self.exists:
            # check if they already have a reset token
            if self.email == '':
                gc.error('Sorry, you are not eligible to use the password reset feature.')
                gc.warning('Only accounts with a valid email address attached can use this feature.')
                gc.msg('Please contact our staff at ' + CONTACT_EMAIL + ' for further assistance.')
            elif self.token == '':
                # generate a token and send it to the user
                self.confirm_email()
                self.save()
                gc.msg('Please check your email for a validation code, then use the \'Reset Password\' feature again.')
            elif self.token_date < gc.string_to_ts(gc.current_time()) - gc.timedelta(days = 1):
                gc.warning('Your reset token has expired. Sending another one...')
                self.confirm_email()
                self.save()
            else:
                token = gc.prompt('Please enter your reset token')
                if token == self.token:
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
                                self.password = hash_password(password, self.name)
                    self.token = ''
                    self.save()
                else:
                    gc.warning('Sorry, that token is not valid. Sending another one...')
                    self.confirm_email()
                    self.save()

        else:
            gc.error('Sorry, that username is not registered.')
        db.close()

    # runs an executable program as a specific user
    def run_program(self, file):

        # check if the computer has enough memory to start the process
        self.computer.lookup()
        file.lookup()
        mem_free = self.computer.get_memory_free()
        file_mem = file.memory

        if file_mem > mem_free:
            gc.error('You have only ' + str(mem_free) + ' MB of RAM free.')
            gc.error('This program requires ' + str(file_mem) + ' MB. Free up memory and try again.')

        # firewalls
        elif file.category == 'FIREWALL':
            gc.warning('Your strongest firewall is automatically running in the background.')

        # antivirus scans
        elif file.category == 'ANTIVIRUS':
            gc.msg('Running virus scan with ' + self.name + '...')
            self.increment_stat('av_count')

        # virus installations
        elif file.category in ['ADWARE', 'SPAMBOT', 'MINER']:
            # get target IP
            text = colored('\n\tINITIATING ' + file.category + ' ', 'green')
            text += colored(file.name, 'yellow')
            text += colored('\n\trun://H4CK/T3H/PL4N37/', 'magenta')
            gc.typewriter(text)
            target_ip = raw_input(colored('\tENTER TARGET IP:', 'red', attrs=['bold', 'reverse']) + ' ')
            target_pw = raw_input(colored('\tENTER TARGET PW:', 'yellow', attrs=['bold', 'reverse']) + ' ')

            # check target
            target = Computer(ip = target_ip)
            target.lookup()
            if target.exists:
                # check if user has already installed this type of virus on target
                already_installed = False
                for t_file in target.get_all_files():
                    if t_file.category == file.category and t_file.is_live and t_file.owner_id == self.id:
                        can_install = True

                # check if user already has an installation process for the same target and virus type
                already_installing = False
                db = Database()
                sql = 'SELECT * FROM processes INNER JOIN files ON processes.file_id = files.id '
                sql += 'WHERE category = %s AND user_id = %s AND target_id = %s'
                args = [file.category, self.id, target.id]
                if len(db.get_query(sql, args)) > 0:
                    already_installing = True
                db.close()

                if already_installed:
                    info_str = '\n\tA ' + file.category + ' IS ALREADY RUNNING ON TARGET. EXITING.\n'
                    gc.typewriter(colored(info_str, 'red'))
                elif already_installing:
                    info_str = '\n\tINSTALLATION OF A ' + file.category + ' IS ALREADY IN PROGRESS ON TARGET. EXITING.\n'
                    gc.typewriter(colored(info_str, 'red'))
                # check if target has enough memory to run the virus
                elif target.get_memory_free() < file.memory:
                    gc.typewriter(colored('\n\tNOT ENOUGH FREE MEMORY ON TARGET. EXITING.\n','red'))
                # check if the password is correct
                elif target.password == target_pw:
                    # start file installation process
                    p = Process(file, self.computer, self, target)
                    gc.typewriter(colored('\n\tTARGET ACQUIRED. LAUNCHING...\n', 'green', attrs = ['reverse']))
                    p.start()
                    p.save()
                else:
                    gc.typewriter(colored('\n\tINVALID PASSWORD. EXITING.\n', 'red'))
            else:
                gc.typewriter(colored('\n\tTARGET NOT FOUND. EXITING.\n', 'red'))

        # password crackers
        elif file.category == 'CRACKER':
            gc.msg('Attempting to crack password...')
            self.increment_stat('cr_count')

        # non-binary files
        else:
            gc.error('That file isn\'t executable and can\'t be run.')

    # concludes a running process without time remaining
    def finish_process(self, process):
        if process.file.category in ['SPAMBOT', 'ADWARE', 'MINER']:
            # get target directory
            install_dir = process.target.root_dir

            # create virus file
            virus = File(gc.gen_virus_name(), install_dir)
            virus.is_live = True
            virus.owner_id = self.id
            virus.type = process.file.type
            virus.category = process.file.category
            virus.size = process.file.size
            virus.memory = process.file.memory
            virus.comment = process.file.comment
            virus.level = process.file.level
            virus.save()
            process.stop()
            gc.success(process.file.name + ' is now running on ' + process.target.ip + '.')
            self.increment_stat('virus_count')

    # changes the email associated with a user's account
    def change_email(self):
        pass

    # changes a user's handle
    def change_handle(self):
        pass

    # changes a user's account password
    def change_password(self):
        gc.msg('Note that you are changing your actual HTP account password.')
        gc.msg('If you want to change your computer\'s root password, use the command chpw.')
        pass

    # increments a user statistic by 1
    def increment_stat(self, stat_name):
        db = Database()
        sql = 'SELECT * FROM user_stats WHERE id = %s'
        args = [self.id]
        result = db.get_query(sql, args)
        sql = ''
        args = [self.id]

        # create user entry if it doesn't exist
        if len(result) == 0:
            sql = 'INSERT into user_stats (id) VALUES (%s)'
            db.post_query(sql, args)

        # increment the appropriate stat
        if stat_name == 'ssh_count':
            sql = 'UPDATE user_stats SET ssh_count = ssh_count + 1 WHERE id = %s'
            db.post_query(sql, args)
        elif stat_name == 'cr_count':
            sql = 'UPDATE user_stats SET cr_count = cr_count + 1 WHERE id = %s'
            db.post_query(sql, args)
        elif stat_name == 'virus_count':
            sql = 'UPDATE user_stats SET virus_count = virus_count + 1 WHERE id = %s'
            db.post_query(sql, args)
        elif stat_name == 'av_count':
            sql = 'UPDATE user_stats SET av_count = av_count + 1 WHERE id = %s'
            db.post_query(sql, args)
        elif stat_name == 'login_count':
            sql = 'UPDATE user_stats SET login_count = login_count + 1 WHERE id = %s'
            db.post_query(sql, args)
        elif stat_name == 'files_edited':
            sql = 'UPDATE user_stats SET files_edited = files_edited + 1 WHERE id = %s'
            db.post_query(sql, args)
        else:
            gc.error(stat_name + ' is not a valid stat.')

        db.close()

    # displays user stats
    def show_stats(self):
        db = Database()
        args = [self.id]

        # get user stats
        sql =  'SELECT * FROM user_stats WHERE id = %s'
        result = db.get_query(sql, args)
        ssh_count = result[0][1]
        cr_count = result[0][2]
        virus_count = result[0][3]
        av_count = result[0][4]
        login_count = result[0][5]
        files_edited = result[0][6]

        # get money stats
        sql = 'SELECT * FROM bank_accounts WHERE owner_id = %s'
        results = db.get_query(sql, args)
        total_money = 0
        for account in results:
            total_money += int(account[4])

        # determine cracker ranking
        sql = 'SELECT COUNT(*) FROM user_stats WHERE cr_count > %s'
        args = [cr_count]
        cr_rank = db.get_query(sql, args)[0][0] + 1

        # determine viruses ranking
        sql = 'SELECT COUNT(*) FROM user_stats WHERE virus_count > %s'
        args = [virus_count]
        virus_rank = db.get_query(sql, args)[0][0] + 1

        # determine money ranking
        sql = ''' SELECT COUNT(*) FROM (SELECT SUM(funds) AS total_funds
            FROM bank_accounts GROUP BY owner_id) AS total_funds
            WHERE total_funds > %s'''
        args = [total_money]
        money_rank = db.get_query(sql, args)[0][0] + 1

        db.close()

        # display stats
        mb = MessageBox('User Statistics')
        mb.add_heading('Ranked Stats')
        cr_str = 'You have cracked ' + colored(str(cr_count), 'cyan') + ' passwords '
        cr_str += '(ranked ' + colored('#' + str(cr_rank), 'yellow') + ' in the world).'
        mb.add_line(cr_str, 2)
        virus_str = 'You have installed ' + colored(str(virus_count), 'cyan') + ' viruses '
        virus_str += '(ranked ' + colored('#' + str(virus_rank), 'yellow') + ' in the world).'
        mb.add_line(virus_str, 2)
        money_str = 'You own ' + colored('$' + str(total_money), 'cyan')
        money_str += ' (ranked ' + colored('#' + str(money_rank), 'yellow') + ' in the world).'
        mb.add_line(money_str, 2)
        mb.add_heading('Misc. Stats')
        mb.add_property('SSH Logins', str(ssh_count))
        mb.add_property('AV Scans Run', str(av_count))
        mb.add_property('Game Logins', str(login_count))
        mb.add_property('Files Edited', str(files_edited))
        mb.display()