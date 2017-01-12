import textwrap

from termcolor import colored

# Message boxes can be used to display info tables in an aesthetic way.
class MessageBox:

    def __init__(self):
        self.title = 'Untitled'     # appears at top
        self.width = 70             # horizontal size in chars
        self.title_color = 'yellow'
        self.border_color = 'green'
        self.label_color = 'cyan'
        self.text_color = 'white'
        self.text = []              # raw text as a list of lines

    # Changes the title at the top of the box
    def set_title(self, title):
        self.title = title

    # Adds a label for a section
    def add_label(self, label):
        pass

    # Adds a property with a name and value to the section
    def add_property(self, name, value):
        label_width = 16

        # get filler space between name and value
        spaces = ''
        i = label_width - len(name)
        while i > 0:
            spaces += ' '
            i -= 1
        text = colored(u'\u2502 ', self.border_color)
        text += colored(name + ':', self.label_color)
        text += spaces
        text += colored(value, self.text_color)

        # add remaining spaces and end line
        spaces = ''
        i = self.width - len(value) - 20
        while i > 0:
            spaces += ' '
            i -= 1
        text += spaces
        text += colored(u'\u2502', self.border_color)

        self.text.append(text)

    # adds a word-wrapped paragraph of text
    def add_long_text(self, text):
        wrapper = textwrap.TextWrapper()
        wrapper.width = self.width - 4
        for line in wrapper.wrap(text):
            # get filler spaces
            spaces = ''
            i = self.width - len(line) - 4
            while i > 0:
                spaces += ' '
                i -= 1

            # add the line
            bordered_line = colored(u'\u2502 ', self.border_color)
            bordered_line += colored(line + spaces, self.text_color)
            bordered_line += colored(u' \u2502', self.border_color)
            self.text.append(bordered_line)

    # Adds a blank line to the box
    def blank_line(self):
        line = u'\u2502'
        i = 0
        while i < self.width - 2:
            line += ' '
            i += 1
        line += u'\u2502'
        self.text.append(line)

    # Adds a horizontal rule to the box
    def hr(self):
        line = u'\u251c'
        i = 0
        while i < self.width - 2:
            line += u'\u2500'
            i += 1
        line += u'\u2524'
        self.text.append(colored(line, self.border_color))

    # Prints the entire message box to console
    def display(self):

        # display the title
        divider_bottom = u'\u2515'
        divider_top = u'\u250d'
        i = 0
        while i < self.width - 2:
            divider_bottom += u'\u2501'
            divider_top += u'\u2501'
            i += 1
        divider_bottom += u'\u2519'
        divider_top += u'\u2511'
        print(colored(divider_top, self.title_color))
        title = u'\u2502 ' + self.title
        i = self.width - len(title) - 1
        while i > 0:
            title += ' '
            i -= 1
        title += u'\u2502'
        print(colored(title, self.title_color))
        print(colored(divider_bottom, self.title_color))

        # display the content
        for line in self.text:
            print(line)

        # close the box
        print(colored(divider_bottom, self.border_color))