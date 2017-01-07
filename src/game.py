#!/usr/bin/python
import re
import signal
import subprocess
import MySQLdb
import random
import pwd
import time

from getpass import getpass
from termcolor import colored

# Handle keyboard interrupt shortcuts
def signal_handler(signum, frame):
    pass # prevent exiting
#signal.signal(signal.SIGTSTP, signal_handler)  # Disable Ctrl-Z
#signal.signal(signal.SIGINT, signal_handler)   # Disable Ctrl-C

def main():
    print("\n")
    login_banner()

    con = connect_database()
    cursor = con.cursor()

    valid_choice = False
    while not valid_choice:
        choice = prompt_num()

        # log in
        if choice == "1":
            login(con)
        # register
        elif choice == "2":
            register(con)
        # reset password
        elif choice == "3":
            pass
        # about
        elif choice == "4":
            pass
        # invalid
        else:
            error("Invalid choice; please try again.")

## Navigation
# Shows a user's profile summary
def profile(con, username):
    show_profile = True
    msg_box("User Summary")
    show_user_summary(con, username)
    while show_profile:
        pass

## Main Menu Options
# Log in an existing account
def login(con):
    cursor = con.cursor()
   # check user credentials
    valid_creds = False
    while not valid_creds:
        username = raw_input("Username: ")
        password = getpass()
        time.sleep(2)
        sql = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(sql, [username, password])
        response = cursor.fetchall()
        if len(response) == 0:
            error("Invalid credentials. Please try again.")
        else:
            success("Credentials validated. Logging in...")
            profile(con, username)

# Register a new user account
def register(con):
    cursor = con.cursor()
    username = ""
    password = ""
    email = ""
    handle = ""
    ip = ""
    msg("\nStarting the account creation process...")
    msg("Your username can be between 4 and 16 characters and must be alphanumeric.")
    valid_user = False
    while not valid_user:
        username = raw_input("Desired Username: ")

        # name cannot be blank
        if username == "":
            error("You must enter a username.")
        # name must be alphanumeric; symbols are rejected prior to database lookup
        elif not username.isalnum():
            error("Your username can only contain letters and numbers.")
        # name must be between 4 and 16 characters
        elif len(username) < 4 or len(username) > 16:
            error("Your username must be between 4 and 16 characters.")
        # name must not already exist in database
        else:
            sql = "SELECT * FROM users WHERE username = %s;"
            cursor.execute(sql, [username])
            response = cursor.fetchall()
            if len(response) > 0:
                error("Sorry, that name is taken. Please choose another.")
            else:
                msg("Username is available!")
                valid_user = True

    # get a valid password
    msg("\n  You can now set a password for your account.")
    valid_password = False
    while not valid_password:
        password = getpass()
        confirm = getpass("Confirm: ")
        if len(password) < 6:
            error("Your password must contain 6 or more characters.")
        elif password != confirm:
            error("Sorry, those passwords didn't match.")
        else:
            valid_password = True

    # get a valid email address
    valid_email = False
    msg("\n  You will need to enter a valid email in case you forget your password.")
    while not valid_email:
        email = raw_input("Email Address: ")
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            # check if email exists in database
            sql = "SELECT * FROM users WHERE email = %s;"
            cursor = con.cursor()
            cursor.execute(sql, [email])
            response = cursor.fetchall()
            if len(response) > 0:
                error("Sorry, that email has already been registered.")
            else:
                valid_email = True
        else:
            error("Sorry, your input was not in the right format for an email address.")

    # get a unique in-game handle
    cursor = con.cursor()
    msg("\n  Finally, you need to choose an in-game handle that others can see.")
    msg("This is separate from your username, and can be changed later.")
    valid_handle = False
    while not valid_handle:
        handle = raw_input("Please enter a handle: ")
        if handle == "":
            error("You must enter a handle.")
        elif not handle.isalnum():
            error("Your handle can only contain letters and numbers.")
        elif len(handle) < 2 or len(handle) > 16:
            error("Your handle must be between 2 and 16 characters.")
        else:
            sql = "SELECT * FROM users WHERE handle = %s;"
            cursor.execute(sql, [handle])
            response = cursor.fetchall()
            if len(response) > 0:
                error("Sorry, that handle is taken. Please choose another.")
            else:
                valid_handle = True

    # create the account
    sql = "INSERT INTO users (username, password, email, handle) VALUES (%s, %s, %s, %s);"
    cursor.execute(sql, [username, password, email, handle])
    success("\n Account " + username + " created!")

    # generate an IP address for the user
    valid_ip = False
    while not valid_ip:
        ip = gen_ip()
        # check if the IP has been assigned already
        sql = "SELECT * FROM computers WHERE ip_address = %s;"
        cursor.execute(sql, [ip])
        response = cursor.fetchall()
        if len(response) == 0:
            valid_ip = True

    # create a computer for the user
    comp_password = gen_password()
    sql = "SELECT id FROM users WHERE username = %s;"
    cursor.execute(sql, [username]) # get user's ID
    owner_id = cursor.fetchone()[0]
    sql = "INSERT INTO computers (ip_address, password, owner_id) VALUES (%s, %s, %s);"
    cursor.execute(sql, [ip, comp_password, int(owner_id)]) # set computer owner to user's ID
    sql = "SELECT id FROM computers WHERE owner_id = %s;"
    cursor.execute(sql, [owner_id]) # get computer's ID
    computer_id = cursor.fetchone()[0]
    sql = "UPDATE users SET computer_id = %s WHERE username = %s;"
    cursor.execute(sql, [computer_id, username]) # update user's computer ID

    # done creating things
    con.commit()
    profile(con, username)

# Establish a connection to MySQL
def connect_database():
    # TODO: move database connections to controller file
    cred_file = open("/htp/dbcreds.txt", 'r')
    u = cred_file.readline()[:-1]
    p = cred_file.readline()[:-1]
    d = "htp"
    con = MySQLdb.connect(host = "localhost",
                          user = u,
                          passwd = p,
                          db = d)
    return con

## Common operations
def show_user_summary(con, username):
    cursor = con.cursor()

    # get computer info
    sql = "SELECT computer_id FROM users WHERE username = %s;"
    cursor.execute(sql, [username])
    computer_id = cursor.fetchone()[0]
    sql = """
          SELECT ip_address, last_login, ram, cpu, hdd, disk_free,
              fw_level, av_level, cr_level, password
          FROM computers
          WHERE id = %s
          """
    cursor.execute(sql, [computer_id])
    response = cursor.fetchall()
    ip_address, last_login, ram, cpu, hdd, disk_free, fw_level, av_level, cr_level, comp_password = response[0]

    # get user's handle
    sql = "SELECT id, handle FROM users WHERE username = %s"
    cursor.execute(sql, [username])
    user_id, handle = cursor.fetchall()[0]

    # get bank account info
    sql = "SELECT funds FROM bank_accounts WHERE owner_id = %s"
    cursor.execute(sql, [user_id])
    response = cursor.fetchall()
    num_accounts = 0
    total_funds = 0
    if len(response) > 0:
        num_accounts = len(response)
        i = 0
        while i < len(response):
            total_funds += int(response[i][0])
            i += 1

    # display all info
    property("RAM", str(ram) + " MB")
    property("CPU", str(cpu) + " MHz")
    property("Disk", str(hdd) + " GB")
    property("Free", str(disk_free) + " GB")
    property("Firewall", "Level " + str(fw_level))
    property("Antivirus", "Level " + str(av_level))
    property("Cracker", "Level " + str(cr_level))
    hr()
    property("IP Address", ip_address)
    property("Comp. Password", str(comp_password))
    hr()
    # add user details
    property("Handle", handle)
    property("Last Login", str(last_login))
    # number of bank accounts
    property("Total Funds", str(total_funds) + " dollars")
    property("# of Accounts", str(num_accounts))

    hr()

# Prompt the user for input
def prompt():
    return raw_input("\nlocalhost:~$ ")

# Prompt for a numeric input
def prompt_num():
    return raw_input("\n# ")

# Generate a random password
def gen_password():
    length = random.randint(8, 12)
    return ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for i in range(length))

# Generate a random IP
def gen_ip():
    w, x, y, z = 0, 0, 0, 0
    while x == 0 and w in (0, 10, 127, 192):
        w = random.randint(1, 255)
        x = random.randint(0, 255)
        y = random.randint(0, 255)
        z = random.randint(0, 255)
    return str(w) + "." + str(x) + "." + str(y) + "." + str(z)

def login_banner():
    print("Welcome to Hack the Planet!")
    print("Choose an option to continue.\n")
    msg("1. Log In")
    msg("2. Register")
    msg("3. Reset Password")

## OUTPUT MESSAGES
# Standard Message
def msg(message):
    print(colored("  " + message, 'cyan'))

# Success Message
def success(message):
    print(colored("  " + message, 'green'))

# Warning Message
def warning(message):
    print(colored("  " +message, 'yellow'))

# Error Message
def error(message):
    print(colored("  " + message, 'red'))

# Info Message
def info(message):
    print(colored("  " + message, 'blue'))

# Horizontal Rule
def hr():
    print(colored("------------------------------------------------------------", "green"))

# Property Message
def property(label, value):
    max_label_length = 16
    spaces = ""
    num_spaces = max_label_length - len(label)
    while num_spaces > 0:
        spaces += " "
        num_spaces -= 1
    print("  " + colored(label + ":", 'cyan') + spaces + colored(value, 'white'))

# Message Box
def msg_box(message):
    box_length = 60
    dashes = ""
    i = box_length
    while i > 0:
        dashes += "-"
        i -= 1
    message_box = dashes + "\n"
    message_box += "| " + message
    i = box_length - len(message) - 3
    while i > 0:
        message_box += " "
        i -= 1
    message_box += "|\n"
    message_box += dashes

    print(colored(message_box, 'yellow'))

if __name__ == '__main__':
    main()

# Prevent user from entering shell
print("Please close this window to disconnect.")
while True:
    pass
