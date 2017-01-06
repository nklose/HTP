import signal

# Handle keyboard interrupt shortcuts
def signal_handler(signum, frame):
    pass # prevent exiting
signal.signal(signal.SIGTSTP, signal_handler)  # Disable Ctrl-Z
signal.signal(signal.SIGINT, signal_handler)   # Disable Ctrl-C

def main():
    print("Hello! You have entered the game loop.")
    
    # Prevent player from exiting game loop
    while True:
        pass

if __name__ == '__main__':
    main()

# Prevent user from entering shell
print("Please close this window to disconnect.")
while True:
    pass