#!/usr/bin/python
from collections import defaultdict

#validate the foreground to background energy ratio

user_last_time = defaultdict(int)
last_time_data = defaultdict(lambda:False)
last_time_energy = defaultdict(lambda:False)
f = open("../energy_summary.txt")

active_time = 0
passive_time = 0

limit = 1000000000

for line in f:
    if limit > 0:
        limit -= 1
    if limit == 0:
        break



    line = line.split()

    (userid, app, time, energy, upbytes, downbytes, networktype) = line
    if networktype == "0":
        continue
#    if userid != "353091053665792":
#        continue

    time = float(time)
    upbytes = int(upbytes)
    downbytes = int(downbytes)
    energy = float(energy)

    if user_last_time[userid] != time and user_last_time[userid] != 0:
#        print time - user_last_time[userid], last_time_energy[userid], last_time_data[userid], time
        if last_time_energy[userid]:
            if last_time_data[userid]:
                active_time += min(time - user_last_time[userid], 1)
#                print "active", active_time
            else:
                passive_time += min(time - user_last_time[userid], 1)
#                print "passive", passive_time, active_time/(active_time+passive_time)
        last_time_data[userid] = False
        last_time_energy[userid] = False 

    if upbytes > 0 or downbytes > 0:
        last_time_data[userid] = True
    if energy > 0:
        last_time_energy[userid] = True


    user_last_time[userid] = time

print active_time, passive_time
