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
        self.msg_text = ">"
        self.logfile = '../data/irc.txt'
        self.log_text = []
        self.get_log_text()
        
        # curses color config
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)

        # start the client
        try:
            curses.wrapper(self.start_loop())
        except Exception as e:
            self.scr.addstr(2, 0, str(e), curses.A_REVERSE)

    # client game loop
    def start_loop(self):
        # start input thread
        it = InputThread(self)
        it.start()
        
        while not self.disconnect:
            # draw top bar
            self.scr.addstr(0, 0, "// Hack the Planet IRC Chat //", curses.A_REVERSE)
            self.draw_line(1)

            # draw channel
            self.scr.addstr(self.scr_height - 1, 0, self.channel, curses.color_pair(1))

            # draw username
            self.scr.addstr(self.scr_height - 1, len(self.channel) + 1, '[' + self.username + "]:")
            self.draw_line(self.scr_height - 2)

            # draw chat messages
            last_line = self.scr_height - 3
            i = 2
            while i <= last_line and i < len(self.log_text) + 2:
                self.scr.addstr(i, 0, self.log_text[i-2])
                i += 1

            # draw user input
            self.scr.addstr(20, 20, self.msg_text)
                
            # get user input
            input_y = self.scr_height - 1
            input_x = len(self.channel) + len(self.username) + 5
            #self.msg_text = self.scr.getstr(input_y, input_x)
            #c = self.scr.getch()
            #if c == ord('q') or c == ord('r'):
            #    self.msg_text += c
                
            # check if the input is a command
            #if self.msg_text[0] == '/':
            #    command = self.msg_text[1:].lower()
            #    if command== 'exit':
            #        self.disconnect = True
            #else:
                # send message to channel
            #    try:
            #        file = open(self.logfile, 'a+')
            #        text = 'S[' + self.get_timestamp() + ']<' + self.username + '> ' + self.msg_text + '\n'
            #        file.write(text)
            #        file.close()
            #    except Exception as e:
            #        print("Error: " + str(e))

            # draw any changes
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

        except Exception as e:
            print("Error:" + str(e))

    def get_timestamp(self):
        ts = time.time()
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

# Receives user input
class InputThread(Thread):
    def __init__(self, sender):
        Thread.__init__(self)
        self.sender = sender
        pass

    def run(self):
        s = self.sender
        while True:
            #self.sender.get_log_text()
            # limit file reads
            input_y = s.scr_height - 1
            input_x = len(s.channel) + len(s.username) + 5
            inp = s.scr.getstr(input_y, input_x)
            print inp
            
if __name__ == '__main__':
    main()
