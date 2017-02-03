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

# File: Bank.py
# A Bank represents a virtual banking company in charge of multiple accounts.

class Bank:
    
    def __init__(self, name, description, min_funds, account_cost, interest_rate):
        self.name = name
        self.description = description
        self.min_funds = min_funds
        self.account_cost = account_cost
        self.interest_rate = interest_rate
