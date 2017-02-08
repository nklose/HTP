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
from User import User
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
        # check if the computer has enough memory to start the process
        self.computer.lookup()
        self.file.lookup()
        mem_free = self.computer.get_memory_free()
        file_mem = self.file.memory

        if file_mem <= mem_free:
            # determine how long the process will take
            seconds = 0
            category = self.file.category
            cpu_modifier = self.computer.cpu / 1024.0
            # virus scans
            if category == 'ANTIVIRUS':
                seconds = AV_MULTIPLIER * self.file.level / (cpu_modifier)
            # password cracking
            elif category == 'CRACKER':
                seconds = CR_MULTIPLIER * self.file.level * self.target.firewall.level / cpu_modifier
            # virus installation
            elif category in ['MINER', 'ADWARE', 'SPAMBOT']:
                seconds = VIRUS_MULTIPLIER * self.file.level * self.target.firewall.level / cpu_modifier
            else:
                gc.error('An error occurred while trying to run the specified program.')

            # set completion timestamp
            self.end_time = gc.ts_to_string(gc.string_to_ts(self.start_time) + datetime.timedelta(seconds = seconds))
            self.save()
            self.exists = True
        else:
            gc.error('You have ' + str(free) + ' MB of memory free, but this requires ' + str(self.file.memory) + '.')

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
                self.start_time = gc.ts_to_string(result[0][4])
                self.end_time = gc.ts_to_string(result[0][5])
                self.memory = int(result[0][6])

                # lookup computer
                self.computer = Computer(id = comp_id)
                self.computer.lookup()

                # lookup user
                self.user = User(id = user_id)
                self.user.lookup()

                # lookup file
                db = Database()
                sql = 'SELECT * FROM files WHERE id = %s'
                args = [file_id]
                result = db.get_query(sql, args)
                if len(result) > 0:
                    file_dir = Directory(int(result[0][2]))
                    file_dir.lookup()
                    file_name = result[0][1]
                    self.file = File(file_name, file_dir)
                    self.file.lookup()
                else:
                    gc.error('The file for this process couldn\'t be found.')

    # saves into the database
    def save(self):
        self.memory = self.file.memory
        db = Database()
        sql = ''
        args = [self.file.id, self.computer.id, self.start_time, self.end_time, self.memory]
        if self.exists:
            args.append(self.id)
            sql = 'UPDATE processes SET file_id = %s, comp_id = %s, started_on = %s, '
            sql += 'finished_on = %s, memory = %s WHERE id = %s'
        else:
            sql = 'INSERT INTO processes (file_id, comp_id, started_on, finished_on, '
            sql += 'memory) VALUES (%s, %s, %s, %s, %s)'
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