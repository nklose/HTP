# This script runs the HTP chat server.
# It authenticates with a single account to an IRC channel and relays messages between
# the channel and the game client via a log file.
# Each line in the log file represents one message.
# The log file is automatically cleared once it reaches its maximum size.
#
# Messages are of the form T[D]<U> M, where:
#   - T is the type of message (R = 'from channel', S = 'to channel', C = 'admin command')
#   - D is the timestamp (format: YYYY-mm-dd HH:MM:SS)
#   - U is the in-game username of the sender
#   - M is the message itself

import time
import socket
import sys
import os

from threading import Thread
from datetime import datetime

server = 'irc.freenode.net'
channel = '##HTP'
port = 6667
nick = '[HTP]'              # username to connect with 
msg_delay = 1               # number of seconds to wait before transmitting messages
connect_delay = 15          # number of seconds to wait for initial connection
logfile = '../data/irc.txt' # file to log messages in 
log_size = 1024 * 1024      # max number of bytes in logfile
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def main():
    sender = Sender()
    receiver = Receiver(sender)
    receiver.start()

# get the current time as a string
def get_timestamp():
    ts = time.time()
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

# convert a  string to a timestamp
def read_timestamp(str):
    if len(str) > 0:
        return datetime.strptime(str, '%Y-%m-%d %H:%M:%S')
    else:
        print("W: Blank line encountered in " + logfile)

# print and write applicable messages to logfile
def log(msg_type, message):
    if msg_type == 'recv':
        text = 'R'
    elif msg_type == 'send':
        text = 'S'
    else:
        text = 'E'
    try:
        file = open(logfile, 'a+')
        text += '[' + get_timestamp() + ']' + message
        file.write(text)
        file.close()
        print(text[:-1])
    except Exception as e:
        print("Error: " + str(e))

# sends a message to the channel
def msg_channel(message):
    irc.send('PRIVMSG ' + channel + ' :' + message + '\r\n')
    print('[SEND] ' + message)

# runs an admin command
def run_command(cmd):
    print('[CMD] ' + cmd)
    cmd_list = cmd.split()
    if cmd_list[0].upper() == 'QUIT':
        disconnect()
    elif cmd_list[0].upper() == 'SAY':
        msg_channel('[Admin] ' + cmd[4:])

# Sends to channel
class Sender(Thread):

    def __init__(self):
        Thread.__init__(self)
        pass

    def run(self):
        last_sent = get_timestamp()
        last_cmd = get_timestamp()
        msg_channel('HTP Bot online. Beep Boop.')
        while True:
            # get lines from file
            lines = []
            try:
                file = open(logfile, 'r+')
                lines = file.readlines()    # TODO: reduce overhead for lookup
                total_size = os.path.getsize(logfile)
                file.close()
                if total_size > log_size:
                    open(logfile, 'w').close()
                    print("I: Log file cleared after reaching max size.")
            except Exception as e:
                print("Error: " + str(e))

            msgs_sent = 0   # number of messages sent to channel in this loop
            cmds_sent = 0   # number of admin commands submitted in this loop

            send_time = ""  # timestamp for messages to send in this loop
            cmd_time = ""   # timestamp for commands to run in this loop

            for line in lines:
                msg_type = line[0]
                msg_time = line[2:21] # timestamp on the message
                if msg_type == 'S': # send to channel
                    ts1 = read_timestamp(last_sent)
                    ts2 = read_timestamp(msg_time)
                    if ts2 > ts1: # if message is new, send it
                        send_time = get_timestamp()
                        username_end = line.find('>')
                        username = line[23:username_end]
                        message = line[username_end + 2:-1]
                        msg_channel('(' + username + ') ' + message)
                        msgs_sent += 1
                        time.sleep(msg_delay)
                elif msg_type == 'C': # run admin command
                    ts1 = read_timestamp(last_cmd)
                    ts2 = read_timestamp(msg_time)
                    if ts2 > ts1 :
                        cmd_time = get_timestamp()
                        command = line[22:]
                        run_command(command)
                        cmds_sent += 1
            if msgs_sent > 0:
                last_sent = send_time # update cutoff
            if cmds_sent > 0:
                last_cmd = cmd_time
            time.sleep(msg_delay)

# Receives from channel
class Receiver(Thread):

    def __init__(self, sender):
        Thread.__init__(self)
        self.sender = sender
        last_sent_time = get_timestamp()
        print('Connecting to chat server...')
        irc.connect((server, 6667))
        irc.send('USER ' + nick + ' ' + nick + ' ' + nick + ' :Hack the Planet!\n')
        irc.send('NICK ' + nick + '\n')
        irc.send('JOIN ' + channel + '\n')
        time.sleep(connect_delay)
        self.sender.start()
        pass

    def run(self):
        while True:
            try:
                text = irc.recv(2040)
                if text.find('PING') != -1:
                    irc.send('PONG ' + text.split() [1] + '\r\n')
                    connected = True
                elif text.find('PRIVMSG') != -1:
                    end = text.find('!')
                    username = text[1:end]
                    start = text.find(channel + ' :')
                    message = text[start + len(channel) + 2:]
                    log('recv', '<' + username + '> ' + message)
                elif text.find('PART') != -1:
                    end = text.find('!')
                    username = text[1:end]
                    log('recv', '[' + username + '] left\n')
                elif text.find('JOIN') != -1:
                    end = text.find('!')
                    username = text[1:end]
                    log('recv', '[' + username + ']' + ' joined\n')
                else:
                    print(text)
            except socket.error:
                break

def disconnect():
    log('send', '<' + nick + '> left')
    print('Disconnecting from chat server...')
    msg_channel('Terminating connection. Beep boop.')
    irc.send('QUIT :The chatbots shall inherit the earth!\r\n')
    time.sleep(5)
    irc.shutdown(socket.SHUT_RDWR)
    irc.close()
    quit()

if __name__ == '__main__':
    main()
