# HTP
A CLI-based hacking strategy game/MMO which is deployed on a Linux SSH server. Clients interact through an SSH client. The game should be hosted on a *nix server.

# Setup
1. Install an SSH server and allow remote connections:
  1.1. Enter the command `sudo apt-get install openssh-server`
  1.2. Make a copy of the config file before changing it:
  
    ```
    sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.factory-defaults
    sudo chmod a-w /etc/ssh/sshd_config.factory-defaults
    ```
3. Install other dependencies with `sudo apt install mysql-server python-dev python-pip python-mysqldb libmysqlclient-dev`. During installation of `mysql-server`, make note of the default database password you set.
4. Log into MySQL with the command `mysql -u [username] -p`, then create the HTP database with `CREATE DATABASE htp;` and exit MySQL.
5. Load the schema into MySQL with `mysql -u [username] -p htp < db.sql`
6. Install necessary Python libraries with `pip install MySQLdb termcolor yagmail`
7. If you are setting up a production server, uncomment lines 36–37 in game.py to disable keyboard interrupts (Ctrl-C, Ctrl-D, Ctrl-Z)
9. Set the `htpuser` and `htppass` environment variables to the database credentials the game should use. For example, to set the `htpuser` password to `secr3t` you could add the line `export htpuser='secr3t'` to your `~/.bashrc` file.
10. Run the game with `python game.py`.

# Email Functionality
Email can optionally be used for password resets. It uses the `yagmail` Python library. If you are enabling email,  `emailuser` environment variable should be set to a valid Gmail address, and `emailpass` should be set to the password for that address.

You may also need to enable [Allow Less Secure Apps](https://support.google.com/accounts/answer/6010255) and [Display Unlock Captcha](https://accounts.google.com/b/0/DisplayUnlockCaptcha) on your Gmail account.

# Deployment
1. Create a UNIX user account on the server, e.g. `guest`.
2. Edit the user's `.bashrc` file to contain only `python /path/to/game.py`
3. Run `touch .hushlogin` in the user's home directory to suppress the login banner
4. Install `lshell` with `sudo apt install lshell`. This is used to restrict access to the file system and shell.
5. Add the `guest` user account to the `lshell` group with `sudo usermod -a -G lshell guest`.
6. Enter the command `sudo chsh -s /usr/bin/lshell guest` to set `lshell` as the default shell for `guest`.
7. Edit the file `/etc/lshell.conf` to look like this:
    ```
    [guest]
    login_script    : "clear && python /path/to/game.py"
    path            : /path/to
    forbidden       : ["ls", "echo", "cd"]
    scp             : 0
    sftp            : 0
    ```
8. Test by connecting to the server via SSH using the username `guest`. Ensure that you are not able to run any shell commands or view system files.

# Future Work
1. Browser-based SSH client which connects to the game
2. Website with connection instructions and information about the game
3. APIs which allow the website to interface with the backend code
4. Fully-featured browser application which can be used in place of the SSH client
