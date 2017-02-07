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

# File: Database.py
# Handles all database operations.

import os
import MySQLdb

class Database:

    def __init__(self):
        self.u = os.environ['htpuser']
        self.p = os.environ['htppass']

        self.d = "htp"
        self.con = MySQLdb.connect(host = 'localhost',
                          user = self.u,
                          passwd = self.p,
                          db = self.d)
        self.cursor = self.con.cursor()

    # search database and return search values
    def get_query(self, sql, args = []):
    	self.cursor.execute(sql, args)
        return self.cursor.fetchall()

    # update tables in the database
    def post_query(self, sql, args = []):
        self.cursor.execute(sql, args)
        response = self.cursor.fetchall()
        self.con.commit()

    def close(self):
        self.con.close()
