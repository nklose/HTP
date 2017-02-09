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

# File: Process.py
# A process is a simulated thread which runs until its completion time, for example
# password cracking or virus scans. It is created by a binary program file and runs
# on a single computer. Each process takes up a certain amount of memory and cannot
# be run if the computer doesn't have enough free memory. The target must be passed
# for target-specific processes such as password cracking or virus installations as
# the duration depends on the target's software.

import datetime

from File import File
from Computer import Computer
from Database import Database
from Directory import Directory

import GameController as gc

# program multipliers
AV_MULTIPLIER = 900   # 15 minutes for L1 on 1 GHz
CR_MULTIPLIER = 30    # 0.5 minutes for L1 against L1 AV on 1 GHz
VIRUS_MULTIPLIER = 60 # 1 minute for L1 against L1 AV on 1 GHz

class Process:

    def __init__(self, file = None, computer = None, user = None, target = None, id = -1):
        self.file = file
        self.target = target
        self.computer = computer
        self.user = user
        self.id = id
        self.start_time = gc.current_time()
        self.end_time = gc.current_time()
        self.exists = False
        self.memory = 0

    def start(self):
    
        # determine how long the process will take
        seconds = 0
        category = self.file.category
        cpu_modifier = self.computer.cpu / 1024.0
        # virus scans
        if category == 'ANTIVIRUS':
            seconds = AV_MULTIPLIER * self.file.level / (cpu_modifier)
        # password cracking
        elif category == 'CRACKER':
            fw_level = 0.5 # for targets with no firewall
            if self.target.firewall.level > 0:
                fw_level = self.target.firewall.level
            seconds = CR_MULTIPLIER * self.file.level * fw_level / cpu_modifier
        # virus installation
        elif category in ['MINER', 'ADWARE', 'SPAMBOT']:
            fw_level = 0.25 # for targets with no firewall
            if self.target.firewall.level > 0:
                fw_level = self.target.firewall.level
            seconds = VIRUS_MULTIPLIER * self.file.level * fw_level / cpu_modifier
        else:
            gc.error('An error occurred while trying to run the specified program.')

        # set completion timestamp
        self.end_time = gc.ts_to_string(gc.string_to_ts(self.start_time) + datetime.timedelta(seconds = seconds))
        self.save()
        self.exists = True

    # looks for an existing object in the database
    def lookup(self):
        # search by id
        if self.id != -1:
            db = Database()
            sql = 'SELECT * FROM processes WHERE id = %s'
            args = [self.id]
            result = db.get_query(sql, args)
            db.close()
            if len(result) > 0:
                self.exists = True
                comp_id = int(result[0][1])
                file_id = int(result[0][2])
                user_id = int(result[0][3])
                target_id = -1
                if not result[0][4] == None:
                    target_id = int(result[0][4])
                self.start_time = gc.ts_to_string(result[0][5])
                self.end_time = gc.ts_to_string(result[0][6])
                self.memory = int(result[0][7])

                # lookup computer
                self.computer = Computer(id = comp_id)
                self.computer.lookup()

                # lookup file
                db = Database()
                sql = 'SELECT * FROM files WHERE id = %s'
                args = [file_id]
                result = db.get_query(sql, args)
                if len(result) > 0:
                    file_dir = Directory(id = int(result[0][2]))
                    file_dir.lookup()
                    file_name = result[0][1]
                    self.file = File(file_name, file_dir)
                    self.file.lookup()
                    if not self.file.exists:
                        gc.error('The process file doesn\'t exist.')
                else:
                    gc.error('The file for this process couldn\'t be found.')

                # lookup user
                self.user.id = user_id
                self.user.lookup()

                # lookup target
                if not target_id == -1:
                    self.target = Computer(id = target_id)
                    self.target.lookup()

    # saves into the database
    def save(self):
        self.memory = self.file.memory
        db = Database()
        sql = ''
        args = [self.file.id, self.computer.id, self.user.id, self.target.id, self.start_time, 
            self.end_time, self.memory]
        if self.exists:
            args.append(self.id)
            sql = 'UPDATE processes SET file_id = %s, comp_id = %s, user_id = %s, target_id = %s, '
            sql += 'started_on = %s, finished_on = %s, memory = %s WHERE id = %s'
        else:
            sql = 'INSERT INTO processes (file_id, comp_id, user_id, target_id, started_on, '
            sql += 'finished_on, memory) VALUES (%s, %s, %s, %s, %s, %s, %s)'
        db.post_query(sql, args)
        self.id = db.get_id()
        self.exists = True
        db.close()

    # get number of seconds remaining until process completes
    def get_time_remaining(self):
        ct = gc.string_to_ts(gc.current_time())
        et = gc.string_to_ts(self.end_time)
        if ct > et:
            return 0
        else:
            return (et - ct).seconds

    # delete this process from the database
    def stop(self):
        db = Database()
        sql = 'DELETE FROM processes WHERE id = %s'
        args = [self.id]
        db.post_query(sql, args)
        db.close()