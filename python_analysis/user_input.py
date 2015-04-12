#!/usr/bin/python

import glob
import zipfile
from collections import defaultdict

TOUCH_SCREEN = 'Touch_Screen'
BACK_KEY = 'Back_Touch_Key'
POWER_KEY = 'Power_Key'
HOME_KEY = 'Home_Key'
PRESS = 'Press'
RELEASE = 'Release'
HORIZ = 'Horizontal'
VERT = 'Vertical'

generate_gestures = True 

class Sessions():
    """ Determines user sessions, defined by periods of user interactivity with >2 min between each user input
    
    TODO: a power button event kills a session and starts a new one, as does pressing the home key"""

    def __init__(self):
        self.user_sessions = defaultdict(list)
        self.user_gestures = defaultdict(list)

        self.last_session_end_time = {} 
        self.last_session_start_time = {}

        self.active_time = {}
        self.num_events = {}

        self.touch_status = {}
        self.tmp_status = {}
        self.last_line = {}

        self.active_time_cutoff = 1
        self.time_interval = 60
        self.session_id = 0

    def get_session_data(self, line, username, min_time, max_time):
        line = line.split()

        # Session data can sometimes get mangled
        try:
            time = float(line[0])
            if time == 0:
                return 
            if time < min_time:
                #print "time to low", time, min_time
                return
            if max_time != -1 and time > max_time:
                #print "time to high", time, max_time
                return
        except:
            return
        
        if (len(line) < 3):
            return
        if (line[1] == TOUCH_SCREEN):
            if (line[2] == PRESS and len(line) != 5):
                return
            if (line[2] == RELEASE and len(line) != 3):
                return
        
        if username not in self.touch_status:
            self.touch_status[username] = ['', False]
            self.tmp_status[username] = [0, 0, -1, -1, -1, -1] # start, end, hori, verti, hori, verti
            self.last_line[username] = ''
        
        if self.touch_status[username][1]:
            # already touch
            if line[1] != self.touch_status[username][0]:
                # key doesn't match
                #print "Touch event log error:", self.touch_status[username][0], line[1], self.last_line[username], line
                if (line[2] == PRESS):
                    self.tmp_status[username][0] = float(line[0])
                    self.tmp_status[username][1] = float(line[0])
                    self.touch_status[username][0] = line[1]
                    self.touch_status[username][1] = True
                    self.tmp_status[username][2] = -1
                    self.tmp_status[username][3] = -1
                    if (line[1] == TOUCH_SCREEN):
                        if (line[3] == VERT):
                            self.tmp_status[username][3] = int(line[4])
                            self.tmp_status[username][5] = int(line[4])
                        if (line[3] == HORIZ):
                            self.tmp_status[username][2] = int(line[4])
                            self.tmp_status[username][4] = int(line[4])
                else:
                    self.touch_status[username][1] = False
            else:
                # key match
                if (line[2] == PRESS):
                    self.tmp_status[username][1] = float(line[0])
                    if (line[1] == TOUCH_SCREEN):
                        if (line[3] == VERT):
                            if (self.tmp_status[username][3] < 0):
                                self.tmp_status[username][3] = int(line[4])
                            self.tmp_status[username][5] = int(line[4])
                        if (line[3] == HORIZ):
                            if (self.tmp_status[username][2] < 0):
                                self.tmp_status[username][2] = int(line[4])
                            self.tmp_status[username][4] = int(line[4])
                elif (line[2] == RELEASE):
                    self.tmp_status[username][1] = float(line[0])
                    self.touch_status[username][1] = False

                    self.user_gestures[username].append([self.touch_status[username][0],
                        self.tmp_status[username][0], self.tmp_status[username][1],
                        self.tmp_status[username][2], self.tmp_status[username][3],
                        self.tmp_status[username][4], self.tmp_status[username][5]])

        elif (line[2] == PRESS):
            # touch not start
            self.touch_status[username][0] = line[1]
            self.touch_status[username][1] = True

            self.tmp_status[username][0] = float(line[0])
            self.tmp_status[username][1] = float(line[0])
            
            self.tmp_status[username][2] = -1
            self.tmp_status[username][3] = -1

            if (line[1] == TOUCH_SCREEN):
                if (len(line) != 5):
                    self.touch_status[username][1] = False
                else:
                    if (line[3] == VERT):
                        self.tmp_status[username][3] = int(line[4])
                        self.tmp_status[username][5] = int(line[4])
                    if (line[3] == HORIZ):
                        self.tmp_status[username][2] = int(line[4])
                        self.tmp_status[username][4] = int(line[4])

        self.last_line[username] = line

        ######################################
        #   SESSION PROCESSING STARTS HERE   #
        ######################################

        if username in self.last_session_end_time and \
                username in self.last_session_start_time:

            if time - self.last_session_end_time[username] > self.time_interval or line[1] == POWER_KEY or line[1] == HOME_KEY:

#                print line
                assert(self.last_session_end_time[username] >= \
                        self.last_session_start_time[username])
                
                estimated_session_time = self.last_session_end_time[username] - \
                        self.last_session_start_time[username] + \
                        self.active_time_cutoff
            
                self.user_sessions[username].append([self.last_session_end_time[username], self.last_session_start_time[username], self.active_time[username], self.session_id, estimated_session_time, self.active_time[username], self.num_events[username], 1]) # last session
                self.session_id += 1
                self.user_sessions[username].append([time, self.last_session_end_time[username], self.active_time[username], self.session_id, -1, -1, -1, 0]) # last nonsession

                self.session_id += 1
                self.active_time[username] = 0
                self.num_events[username] = 0
                self.last_session_start_time[username ] = time

        if username not in self.last_session_start_time:
            self.active_time[username] = 0
            self.num_events[username] = 0
            self.last_session_start_time[username] = time

        if username in self.last_session_end_time and \
                time - self.last_session_end_time[username] <= \
                self.active_time_cutoff:

            self.active_time[username] += time - self.last_session_end_time[username]
        else:
            self.active_time[username] += self.active_time_cutoff

        self.last_session_end_time[username] = time
        self.num_events[username] += 1

        #print self.last_session_end_time[username], self.last_session_start_time[username], username

    def generate_session_log(self, generate_gestures, limit=-1):
        load_data(self.get_session_data, limit)
        f = open("/z/user-study-imc15/PACO/user_session_summary.txt", "w")
        for k, v in self.user_sessions.iteritems():
            for item in v:
                print >>f, k, item[1], item[0], item[2], item[3], item[4], item[5], item[6], item[7]
#                print  k, item[1], item[0], item[2], item[3], item[4]
        
        if generate_gestures:
            f2 = open("/z/user-study-imc15/PACO/gesture_summary.txt", "w")
            
            for k, v in self.user_gestures.iteritems():
                for item in v:
                    print >>f2, k, item[0], item[1], item[2], item[3], item[4], item[5], item[6]

            f2.close()

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
                #print line

            file_lines.sort()
            for line in file_lines:
                process_function(line, username, min_time, max_time)


if __name__ == "__main__":
    sessions = Sessions()
    limit = -1
#    if generate_gestures:
#        limit = 236660
    sessions.generate_session_log(generate_gestures, limit)
#    validation = Validation()
#    validation.validate()


