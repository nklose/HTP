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

# File: ChatSession.py
# A ChatSession represents a single User's connection to the chat server.

import os
import time
import curses
import curses.textpad

from threading import Thread
from datetime import datetime

def main():
    cs = ChatSession('TestUser')

class ChatSession():
    def __init__(self, username):
        os.environ.setdefault('ESCDELAY', '25') # shorten esc delay
        self.username = username

        # set up IRC
        self.channel = "##HTP"

        # set up curses
        self.scr = curses.initscr()
        self.disconnect = False
        curses.start_color()
        self.scr_height, self.scr_width = self.scr.getmaxyx()
        self.chatbar = curses.newwin(5, self.scr_height - 1, 5, 10)
        self.msg_text = ''
        self.logfile = '../data/irc.txt'
        self.log_text = []
        
        # curses color config
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)

        # start the client
        try:
            curses.wrapper(self.start_loop())
        except Exception as e:
            self.scr.addstr(2, 0, str(e), curses.A_REVERSE)

    # client game loop
    def start_loop(self):
        while not self.disconnect:
            self.msg_text = ''

            # draw top bar
            self.scr.addstr(0, 0, '// Hack the Planet IRC Chat // (type /exit to quit)', 
                curses.A_REVERSE)
            self.draw_line(1)

            # draw channel
            self.scr.addstr(self.scr_height - 1, 0, self.channel, curses.color_pair(1))

            # draw username
            self.scr.addstr(self.scr_height - 1, len(self.channel) + 1, '[' + self.username + ']:')
            self.draw_line(self.scr_height - 2)

            # draw latest chat messages
            self.get_log_text()
            i = self.scr_height - 3
            log_line = len(self.log_text) - 1
            while i > 1:
                self.scr.addstr(i, 0, self.log_text[log_line])
                log_line -= 1
                i -= 1
                
            # get user input
            input_y = self.scr_height - 1
            input_x = len(self.channel) + len(self.username) + 5
            self.msg_text = self.scr.getstr(input_y, input_x)

            # check if input is blank  
            if self.msg_text == '':
                pass
            # check if the input is a command
            elif self.msg_text[0] == '/':
                command = self.msg_text[1:].lower()
                if command== 'exit':
                    self.disconnect = True
            else:
                # send message to channel
                try:
                    file = open(self.logfile, 'a+')
                    text = 'S[' + self.get_timestamp() + ']<' + self.username + '> ' + self.msg_text + '\n'
                    file.write(text)
                    file.close()
                except Exception as e:
                    print("Error: " + str(e))

            # draw any changes
            self.scr.clear()
            self.scr.refresh()
                    
       # reset to standard terminal and exit
        curses.endwin()

    # draws a horizontal line at a given y-coordinate
    def draw_line(self, y):
        line = ''
        i = 0
        while i < self.scr_width:
            line += '-'
            i += 1
        self.scr.addstr(y, 0, line)

    def get_log_text(self):
        self.log_text = []
        try:
            f = open(self.logfile, 'r+')
            self.log_text = f.readlines()
            f.close()

            # TODO: parse lines

        except Exception as e:
            print("Error:" + str(e))

    def get_timestamp(self):
        ts = time.time()
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            
if __name__ == '__main__':
    main()
