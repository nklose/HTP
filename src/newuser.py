#!/usr/bin/python

import signal
import subprocess
import MySQLdb

from termcolor import colored

# Handle keyboard interrupt shortcuts
def signal_handler(signum, frame):
    pass # prevent exiting
#signal.signal(signal.SIGTSTP, signal_handler)  # Disable Ctrl-Z
#signal.signal(signal.SIGINT, signal_handler)   # Disable Ctrl-C

def main():
    print("\n")
    msg("Welcome to Terminal! You must create an account before playing this game.")
    msg("If you have forgotten your password, please email spartandominion@gmail.com.")
    msg("Your username can be between 4 and 16 characters and must be alphanumeric.")

    db = connect_database()
    cursor = db.cursor()

    username = ""
    valid_user = False

    while not valid_user:
        username = raw_input("\nDesired Username: ")
        msg("You entered " + username + ".")
        
        # look up username in database
        sql = "SELECT * FROM users WHERE username = %s"
        cursor.execute(sql, [username])
        response = cursor.fetchall()
                
        # name cannot be blank
        if username == "":
            error("You must enter a username.")
        # name must be alphanumeric
        elif not username.isalnum():
            error("Your username can only contain letters and numbers.")
        # name must be between 4 and 16 characters
        elif len(username) < 4 or len(username) > 16:
            error("Your username must be between 4 and 16 characters.")
        # name must not already exist in database
        elif len(response) > 0:
            error("Sorry, that name is taken. Please choose another.")
        else:
            msg("Username is available! Please enter your password:")

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

## OUTPUT MESSAGES
# Standard Message
def msg(message):
    print(colored("\t" + message, 'white'))

# Success Message
def success(message):
    print(colored("\t" + message, 'green'))

# Warning Message
def warning(message):
    print(colored("\t" +message, 'yellow'))

# Error Message
def error(message):
    print(colored("\t" + message, 'red'))

if __name__ == '__main__':
    main()

# Prevent user from entering shell
print("Please close this window to disconnect.")
while True:
    pass
