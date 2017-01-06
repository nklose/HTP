#!/usr/bin/python
import re
import signal
import subprocess
import MySQLdb
import random

from getpass import getpass
from termcolor import colored

# Handle keyboard interrupt shortcuts
def signal_handler(signum, frame):
    pass # prevent exiting
#signal.signal(signal.SIGTSTP, signal_handler)  # Disable Ctrl-Z
#signal.signal(signal.SIGINT, signal_handler)   # Disable Ctrl-C

def main():
    print("\n")
    success("Welcome to Terminal! You must create an account before playing this game.")
    success("If you have forgotten your password, please email spartandominion@gmail.com.")
    
    db = connect_database()
    cursor = db.cursor()

    username = ""
    password = ""
    email = ""
    handle = ""
    ip = ""

    msg("\n  Your username can be between 4 and 16 characters and must be alphanumeric.")
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
        if len(password) <= 6:
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
            cursor.execute(sql, [email])
            response = cursor.fetchall()
            if len(response) > 0:
                error("Sorry, that email has already been registered.")
            else:
                valid_email = True
        else:
            error("Sorry, your input was not in the right format for an email address.")

    # get a unique in-game handle
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
            msg("You have been assigned IP address " + ip + ".")
    
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
    success("Please close this session and reconnect with your new credentials.")
    
    # commit changes and close the database connection
    db.commit()
    db.close()

    # Prevent player from exiting game loop
    while True:
        pass

# Establish a connection to MySQL
def connect_database():
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
# Generate a random password for a computer or account
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

if __name__ == '__main__':
    main()

# Prevent user from entering shell
print("Please close this window to disconnect.")
while True:
    pass
