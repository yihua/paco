#!/usr/bin/python

import glob
import zipfile
from collections import defaultdict


class Sessions():
    """ Determines user sessions, defined by periods of user interactivity with >2 min between each user input"""

    def __init__(self):
        self.user_sessions = defaultdict(list)

        self.last_session_end_time = {} 
        self.last_session_start_time = {}

        self.active_time = 0

        self.active_time_cutoff = 1
        self.time_interval = 60
        self.session_id = 0

    def get_session_data(self, line, username, min_time, max_time):
        line = line.split()

        if username != "353091053686046": # XXX
            return 
        # Session data can sometimes get mangled
        try:
            time = float(line[0])
            if time == 0:
                return 
            if time < min_time:
                print "time to low", time, min_time
                return
            if max_time != -1 and time > max_time:
                print "time to high", time, max_time
                return
        except:
            return

        if username in self.last_session_end_time and username in self.last_session_start_time:
            if time - self.last_session_end_time[username] > self.time_interval:

#                print line
                assert(self.last_session_end_time[username] >= self.last_session_start_time[username])
                
                estimated_session_time = self.last_session_end_time[username] - self.last_session_start_time[username] + self.active_time_cutoff
            
                self.user_sessions[username].append([self.last_session_end_time[username], self.last_session_start_time[username], self.active_time, self.session_id, estimated_session_time]) 
                self.session_id += 1
                self.active_time = 0
                self.last_session_start_time[username ] = time

        if username not in self.last_session_start_time:
            self.active_time = 0
            self.last_session_start_time[username] = time

        if username in self.last_session_end_time and \
                time - self.last_session_end_time[username] <= self.active_time_cutoff:
            self.active_time += time - self.last_session_end_time[username]
        else:
            self.active_time += self.active_time_cutoff

        self.last_session_end_time[username] = time
        print self.last_session_end_time[username], self.last_session_start_time[username], username


    def generate_session_log(self, limit=-1):
        load_data(self.get_session_data, limit)
        f = open("/z/user-study-imc15/PACO/user_session_summary.txt", "w")
        for k, v in self.user_sessions.iteritems():
            for item in v:
                print >>f, k, item[1], item[0], item[2], item[3]
#                print  k, item[1], item[0], item[2], item[3], item[4]

class Validation():
    """ Examines log formats, for exploratory purposes """
    def __init__(self):
        self.entry_types = defaultdict(set)

    def validation_function(self, line, username):
        line = line.split()
        time = float(line[0])
        try:
            log_type = line[1]
        except:
            print line
            return
        for i in range(2, len(line)):
            try:
                int(line[i])
            except:
                if line[i] not in self.entry_types[log_type]:
                    print line
                self.entry_types[log_type].add(line[i])

    def validate(self):

        load_data(self.validation_function, 1000)
        for k, v in self.entry_types.iteritems():
            print k, v

def load_data(process_function, limit=-1):
    """ Generic function for loading user input data.
    
    Also does some validation.

    process_function: a function of the form function(line, username, min_time, max_time)."""

    files = []

    # This file must be complete and sorted
    f = open("/nfs/beirut1/userstudy/2nd_round/non_empty_user_input_list")
#    f = open("temp")
    for line in f.readlines():
        files.append("/nfs/beirut1/userstudy/2nd_round/" + line[2:].strip())
    f.close()

# First, organize files by user and then by time:
    sorted_files = defaultdict(list)
    for filename in files:
        username = filename.split("/")[-2].split("-")[-1]
        sorted_files[username].append(filename)

    files_processed = 0

    for username, file_list in sorted_files.iteritems():

        file_list.sort()
        for (i, filename) in enumerate(file_list):

            if limit != -1:
                if limit== 0:
                    break
                limit -= 1

            files_processed += 1

            if files_processed % 1000 == 0:
                print "processed", files_processed, "files"

            min_time = float(filename.split("/")[-2].split("-")[1])

            max_time = -1
            if i + 1 < len(file_list):
                max_time = float(file_list[i+1].split("/")[-2].split("-")[1])
    
#            print filename
            f = open(filename)

            file_lines = []
            for line in f.readlines():
                if "****" in line:
                    continue
                file_lines.append(line)

            file_lines.sort()
            for line in file_lines:
                process_function(line, username, min_time, max_time)


if __name__ == "__main__":
    sessions = Sessions()
    sessions.generate_session_log()
#    validation = Validation()
#    validation.validate()


