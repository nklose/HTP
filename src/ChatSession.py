import curses

def main():
    cs = ChatSession('TestUser')

class ChatSession():
    def __init__(self, username):
        self.username = username
        self.scr = curses.initscr()
        self.disconnect = False
        curses.noecho()
        curses.cbreak()
        self.scr.keypad(1)
        self.width = 40
        self.height = 50
        self.input_x = 20
        self.input_y = 7
        self.scr_height, self.scr_width = self.scr.getmaxyx()
        self.win = curses.newwin(self.height, self.width, self.input_y, self.input_x)
        while not self.disconnect:
            self.scr.addstr(self.scr_height - 1, 1, '[' + self.username + "]:", curses.A_REVERSE)
            self.draw_line(self.scr_height - 2)
            self.scr.refresh()

    def draw_line(self, y):
        line = ''
        i = 0
        while i < self.scr_width:
            line += '-'
            i += 1
        self.scr.addstr(y, 0, line)
            
if __name__ == '__main__':
    main()
