import os
import MySQLdb

import GameController as gc

class Database:

    def __init__(self):
        self.u = os.environ['htpuser']
        self.p = os.environ['htppass']

        self.d = "htp"
        self.con = MySQLdb.connect(host = "localhost",
                          user = self.u,
                          passwd = self.p,
                          db = self.d)
        self.cursor = self.con.cursor()

    # search database and return search values
    def get_query(self, sql, args):
    	self.cursor.execute(sql, args)
        return self.cursor.fetchall()

    # update tables in the database
    def post_query(self, sql, args):
        self.cursor.execute(sql, args)
        response = self.cursor.fetchall()
        self.con.commit()

    def close(self):
        self.con.close()
