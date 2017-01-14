import os
import curses
import curses.textpad

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
        self.msg_text = ""
        
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
            # draw top bar
            self.scr.addstr(0, 0, "// Hack the Planet IRC Chat //", curses.A_REVERSE)
            self.draw_line(1)
            self.scr.addstr(2, 0, '[' + self.username + '] ' + str(self.msg_text))
           
            # draw channel
            self.scr.addstr(self.scr_height - 1, 0, self.channel, curses.color_pair(1))

            # draw username
            self.scr.addstr(self.scr_height - 1, len(self.channel) + 1, '[' + self.username + "]:")
            self.draw_line(self.scr_height - 2)

            # get user input
            input_y = self.scr_height - 1
            input_x = len(self.channel) + len(self.username) + 5
            self.msg_text = self.scr.getstr(input_y, input_x)
            self.scr.clear()

            self.scr.refresh()

            # check if the input is a command
            if self.msg_text[0] == '/':
                command = self.msg_text[1:].lower()
                if command== 'exit':
                    self.disconnect = True
            else:
                # send message to channel
                pass
            
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
            
if __name__ == '__main__':
    main()
