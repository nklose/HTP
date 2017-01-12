# HTP
A CLI-based hacking strategy game/MMO which is deployed on a Linux SSH server. Clients interact through an SSH client. The game should be hosted on a *nix server.

# Deployment
1. Install an SSH server and allow remote connectionse
  
  1.1. Open a terminal and type `sudo apt-get install openssh-server`
  
  1.2. Make a copy of the config file before changing it:
  
    ```
    sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.factory-defaults
    sudo chmod a-w /etc/ssh/sshd_config.factory-defaults
    ```
3. Install other dependencies with `sudo apt-get install mysql-server python-dev python-pip python-mysqldb libmysqlclient-dev`. During installation of `mysql-server`, make note of the default database password you set.
4. Log into MySQL with the command `mysql -u [username] -p`, then create the HTP database with `CREATE DATABASE htp;` and exit MySQL.
5. Load the schema into MySQL with `mysql -u [username] -p htp < db.sql`
6. Install necessary Python libraries with `pip install MySQLdb termcolor`
7. Create a file `/htp/dbcreds.txt` with your database username on the first line and your password on the second line.
8. If desired, uncomment the lines in .py scripts that disable keyboard shortcuts like Ctrl-C or Ctrl-Z
9. Run the game with `python game.py`.

# Testing
1. Create a UNIX user account on the server for testing, e.g. `game`
2. Edit the user's `.bashrc` file to contain only `python /path/to/game.py`
3. Run `touch .hushlogin` in the user's home directory to suppress the login banner
4. Connect to the server via SSH and the user account you created

# Future Work
Once the CLI-only version is functional, it can be deployed for web browsers via a browser-based SSH client, and later via an API and fully-featured website.
