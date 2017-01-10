class Database:

    def __init__(self):
        self.cred_file = open("/htp/dbcreds.txt", 'r')
        self.u = cred_file.readline()[:-1]
        self.p = cred_file.readline()[:-1]
        self.d = "htp"
        self.con = MySQLdb.connect(host = "localhost",
                          user = u,
                          passwd = p,
                          db = d)
        self.cursor = con.cursor()

    def get_query(self, sql, args):
        self.cursor.execute(sql, args)
        response = self.cursor.fetchall()
        self.con.close()

        return response
        
    def post_query(self, sql, username):
        pass
