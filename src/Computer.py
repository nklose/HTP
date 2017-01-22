import GameController as gc

from Database import Database

class Computer:

    def __init__(self, owner_id = -1):
        self.owner_id = owner_id
        self.ram = 512
        self.cpu = 512
        self.hdd = 1
        self.disk_free = 512
        self.fw_level = 1
        self.av_level = 1
        self.cr_level = 1
        self.ip = '0.0.0.0'
        self.password = ''
        self.bank_id = None
        self.domain_name = None
        self.id = -1
        self.last_login = gc.current_time()
        self.exists = False

    # gets information from database for a specific computer IP if it exists
    def lookup(self):
        db = Database()
        sql = ''
        args = []
        # search by IP
        if self.ip != '0.0.0.0':
            sql = 'SELECT * FROM computers WHERE ip = %s'
            args = [self.ip]
        # search by ID
        elif self.id != -1:
            sql = 'SELECT * FROM computers WHERE id = %s'
            args = [self.id]
        # search by owner's ID
        elif self.owner_id != -1:
            sql = 'SELECT * FROM computers WHERE owner_id = %s'
            args = [self.owner_id]
        result = db.get_query(sql, args)
        if len(result) > 0:
            self.exists = True
            self.id = int(result[0][0])
            self.ip = result[0][1]
            self.password = result[0][2]
            self.domain_name = result[0][3]
            self.owner_id = int(result[0][4])
            self.last_login = gc.ts_to_string(result[0][5])
            if result[0][6] != None:
                self.bank_id = int(result[0][6])
            else:
                self.bank_id = None
            self.ram = int(result[0][7])
            self.cpu = int(result[0][8])
            self.hdd = int(result[0][9])
            self.disk_free = int(result[0][10])
            self.fw_level = int(result[0][11])
            self.av_level = int(result[0][12])
            self.cr_level = int(result[0][13])
        db.close()

    # writes the current object's state to the database
    def save(self):
        db = Database()

        sql = ''

        if not self.exists:
            sql = 'INSERT INTO computers (ip, password, domain_name, owner_id, last_login, bank_id, '
            sql += 'ram, cpu, hdd, disk_free, fw_level, av_level, cr_level) VALUES '
            sql += '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            args = [self.ip, self.password, self.domain_name, self.owner_id,
                self.last_login, self.bank_id, self.ram, self.cpu, self.hdd, self.disk_free,
                self.fw_level, self.av_level, self.cr_level]
            self.exists = True
        else:
            sql = 'UPDATE computers SET password = %s, owner_id = %s, last_login = %s, '
            sql += 'bank_id = %s, ram = %s, cpu = %s, hdd = %s, disk_free = %s, fw_level = %s, '
            sql += 'av_level = %s, cr_level = %s WHERE ip = %s'
            args = [self.password, self.domain_name, self.owner_id,
                self.last_login, self.bank_id, self.ram, self.cpu, self.hdd, self.disk_free,
                self.fw_level, self.av_level, self.cr_level, self.ip]
        db.post_query(sql, args)
        db.close()
