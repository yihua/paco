#!/usr/bin/python


from collections import defaultdict
from scipy.stats.stats import pearsonr

import operator
import c_session

import numpy

flows = c_session.CFlow()
flows.load_data()

last_time = defaultdict(None)
all_intertimes = defaultdict(int)
all_intertimes_list = []
total_intertimes = 0


for item in flows.data:
    userid = item["userID"]
    is_encrypted = (len(item["host"]) == 0)

    time = item["start_time"]

    energy_active = item["active_energy"]
    energy_tail = item["passive_energy"]

    fg_log = item["fg_log"]
    fg_code = -1
    if len(fg_log) > 0:
        fg_log.sort(key=operator.itemgetter(1))
        fg_code = fg_log[0][0]


    foreground = (fg_code == 100 or fg_code == 200)
    intertime = 0
    if userid in last_time:
        intertime = time - last_time[userid]
    last_time[userid] = time

    if intertime < 1 or intertime > 86400:
        continue
    if not foreground:
        all_intertimes[int(intertime)] += int(intertime)
        all_intertimes_list.append(int(intertime))
        total_intertimes += int(intertime)

times = all_intertimes.keys()
times.sort()
cumulative = 0
print numpy.mean(all_intertimes_list), numpy.median(all_intertimes_list)

f = open("output_files/intertime_all_cdf.txt", "w")
for t in times:
    cumulative += all_intertimes[t]
    print >>f, float(cumulative)/total_intertimes, t 
f.close()    

