# HTP
A CLI-based hacking strategy game/MMO which is deployed on a Linux SSH server. Clients interact through an SSH client. 

# Deployment
1. Install Python 2.x on a Linux server
2. Install an SSH server and allow remote connections
3. Uncomment the lines in .py scripts that disable keyboard shortcuts like Ctrl-C or Ctrl-Z

# Testing
1. Create a UNIX user account on the server for testing, e.g. `testuser`
2. Edit the user's `.bashrc` file to contain only `python /path/to/game.py`
3. Run `touch .hushlogin` in the user's home directory to suppress the login banner
4. Connect to the server via SSH and the user account you created

# Future Work
Once the CLI-only version is functional, it can be deployed for web browsers via a browser-based SSH client, and later via an API and fully-featured website.