# Allows communication with IRC server.
import socket
import sys

class ChatSession:

    def __init__(self, nick):
        self.server = 'irc.freenode.net'
        self.channel = '#spartandominion'
        self.port = 6667
        self.nick = nick
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        print('Connecting to chat server...')
        self.irc.connect((self.server, 6667))
        self.irc.send('USER ' + self.nick + ' ' + self.nick + ' ' + self.nick + ' :Beep boop!\n')
        self.irc.send('NICK ' + self.nick + '\n')
        self.irc.send('JOIN ' + self.channel + '\n')

        connected = True

        while connected:
            text = self.irc.recv(2040)
            if text.find('PRIVMSG'):
                print text
            if text.find('PING') != -1:
                self.irc.send('PONG ' + text.split() [1] + '\r\n')

        disconnect()

    def disconnect(self):
        print('Disconnecting from chat server...')