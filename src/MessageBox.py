from termcolor import colored

# Message boxes can be used to display info tables in an aesthetic way.
class MessageBox:

    def __init__(self):
        self.title = 'Untitled'     # appears at top
        self.width = 60             # horizontal size in chars
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
        text = colored('| ', self.border_color)
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
        text += colored('|', self.border_color)

        self.text.append(text)

    # Adds a horizontal rule to the box
    def hr(self):
        line = ''
        i = 0
        while i < self.width:
            line += '-'
            i += 1
        self.text.append(colored(line, self.border_color))

    # Prints the entire message box to console
    def display(self):

        # display the title
        divider = ''
        i = 0
        while i < self.width:
            divider += '-'
            i += 1
        print(colored(divider, self.title_color))
        title = '| ' + self.title
        i = self.width - len(title) - 1
        while i > 0:
            title += ' '
            i -= 1
        title += '|'
        print(colored(title, self.title_color))
        print(colored(divider, self.title_color))

        # display the content
        for line in self.text:
            print(line)

        # close the box
        print(colored(divider, self.border_color))