# Allows communication with IRC server.
# Users share a single IRC account to avoid waiting for a connection to the network.
import socket
import sys
import threading
import os
import time

from datetime import datetime

server = 'irc.freenode.net'
channel = '##HTP'
port = 6667
nick = '[HTP2]'         # username to connect with
last_sent_time = ""
ratelimit = 10          # max number of messages to transmit per second
msg_delay = 2           # number of seconds to wait before transmitting messages
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
thread_send = []
thread_recv = []
num_threads = 10        # max number of threads

def main():
    # connect to server
    last_sent_time = get_timestamp()
    print('Connecting to chat server...')
    irc.connect((server, 6667))
    irc.send('USER ' + nick + ' ' + nick + ' ' + nick + ' :Beep boop!\n')
    irc.send('NICK ' + nick + '\n')
    irc.send('JOIN ' + channel + '\n')

    for loop_1 in range(num_threads):
        thread_send.append(threading.Thread(target = send_msg))
        thread_send[-1].start()

    for loop_2 in range(num_threads):
        thread_recv.append(threading.Thread(target = recv_msg))
        thread_recv[-1].start()

def get_timestamp():
    ts = time.time()
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def read_timestamp(str):
    return datetime.strptime(str, '%Y-%m-%d %H:%M:%S')

# Send a message to IRC
def send_msg():
    while True:
        # read X lines from end of file
        time.sleep(msg_delay)
        file = open('../data/irc.txt')
        lines = file.readlines()    # TODO: reduce overhead for lookup

        # parse each line
        for line in lines:
            if len(line) > 21:
                msg_type = line[0]  # 'S' for send to channel, 'R' for receive
                msg_time = line[2:21]
                ts1 = read_timestamp(last_sent_time)
                ts2 = read_timestamp(msg_time)
                print("LST: " + last_sent_time)
                if ts2 > ts1 and msg_type == 'S':
                    username_end = line.find('>')
                    username = line[23:username_end]
                    message = line[username_end + 2:]
                    log('send', '<' + nick + '> ' + message)
                    irc.send('PRIVMSG ' + channel + ' ' + message + '\r\n')
                    last_sent_time = get_timestamp()

# Receive a message from IRC
def recv_msg():
    while True:
        try:
            text = irc.recv(2040)
            if text.find('PING') != -1:
                irc.send('PONG ' + text.split() [1] + '\r\n')
            elif text.find('PRIVMSG') != -1:
                end = text.find('!')
                username = text[1:end]
                start = text.find(channel + ' :')
                message = text[start + len(channel) + 2:]
                log('recv', '<' + username + '> ' + message)
            elif text.find('PART') != -1:
                end = text.find('!')
                username = text[1:end]
                log('recv', '[' + username + '] left')
            elif text.find('JOIN') != -1:
                end = text.find('!')
                username = text[1:end]
                log('recv', '[' + username + ']' + ' joined')
            else:
                print(text)
        except socket.error:
            break

# print and write applicable messages to logfile
def log(msg_type, message):
    file = open('../data/irc.txt', 'a')
    if msg_type == 'recv':
        text = 'R'
    elif msg_type == 'send':
        text = 'S'
    else:
        text = 'E'
    text += '[' + get_timestamp() + ']' + message
    file.write(text)
    print(text)

def disconnect():

    log('send', '<' + nick + '> left')
    print('Disconnecting from chat server...')
    irc.send('QUIT :Bye!\r\n')
    irc.shutdown(socket.SHUT_RDWR)
    irc.close()
    quit()

if __name__ == '__main__':
    main()