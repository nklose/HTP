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

# File: Email.py
# An Email represents a single private message sent from one user to another.

class Email:
    
    def __init__(self, content, subject, server_id, recipient_email, sender_email):
        self.content = content
        self.subject = subject
        self.server_id = server_id
        self.recipient_email = recipient_email
        self.sender_email = sender_email

