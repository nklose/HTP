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

# File: TextEditor.py
# The TextEditor object allows users to edit text files in-game.

import curses

import GameController as gc

from curses.textpad import Textbox, rectangle

from File import File
from Directory import Directory

class TextEditor:
    def __init__(self, file):
        self.file = file
        self.scr = curses.initscr()
        self.scr.border()
        self.scr_height, self.scr_width = self.scr.getmaxyx()
        self.text_win = curses.newwin(self.scr_height - 1, self.scr_width, 1, 0)
        self.file_text = file.content
        self.text_win.addstr(self.file_text)
        curses.noecho()
        #curses.start_color()
        #curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)

        if self.file.exists:
            self.start_editor()
        else:
            curses.endwin()
            gc.error('An error occurred while editing this file.')

    def start_editor(self):
        try:
            # draw the top bar
            top_bar = 'Editing ' + self.file.name + ' [press Ctrl+G to save and close]'
            i = len(top_bar)
            while i < self.scr_width:
                top_bar += ' '
                i += 1
            self.scr.addstr(0, 0, top_bar, curses.A_REVERSE)
            self.scr.refresh()
            
            # let the user edit th efile
            box = Textbox(self.text_win)
            box.edit()

            # get the file contents
            self.file_text = box.gather()
        finally:
            # return to the game
            curses.endwin()
            gc.clear()
            self.file.content = self.file_text
