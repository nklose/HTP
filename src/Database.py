import MySQLdb

class Database:

    def __init__(self):
        self.cred_file = open("/htp/dbcreds.txt", "r")
        self.u = self.cred_file.readline()[:-1]
        self.p = self.cred_file.readline()[:-1]
        self.d = "htp"
        self.con = MySQLdb.connect(host = "localhost",
                          user = self.u,
                          passwd = self.p,
                          db = self.d)
        self.cursor = self.con.cursor()

    # search database and return search values
    def get_query(self, sql, args):
	self.cursor.execute(sql, args)
        
        # fetch one if only one item in args
        if len(args) == 1:
            response = self.cursor.fetchone()        
        # fetch all otherwise
        elif len(args) > 1:     
            response = self.cursor.fetchall()
        return response
    
    # update tables in the database
    def post_query(self, sql, args):
        self.cursor.execute(sql, args)
        response = self.cursor.fetchall()
        self.con.commit()

    def close(self):
        self.con.close()
