#!/usr/bin/python

import glob
import zipfile
from collections import defaultdict


class 

class Validation():
    """ Examines log formats, for exploratory purposes """
    def __init__(self):
        self.entry_types = defaultdict(set)

    def validation_function(self, line):
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

    files = []
    f = open("/nfs/beirut1/userstudy/2nd_round/non_empty_user_input_list")
    for line in f.readlines():
        files.append("/nfs/beirut1/userstudy/2nd_round/" + line[2:].strip())
    f.close()

    for filename in files:
        if limit != -1:
            if limit== 0:
                break
            limit -= 1

        f = open(filename)
        for line in f.readlines():
            if "****" in line:
                continue
            process_function(line)


if __name__ == "__main__":
    validation = Validation()
    validation.validate()
