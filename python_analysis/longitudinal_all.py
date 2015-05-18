#!/usr/bin/python

import c_session
import operator
import sys
import numpy
from collections import defaultdict

by_flow = True 


content_size_by_user = defaultdict(lambda:defaultdict(int))
content_energy_by_user = defaultdict(lambda:defaultdict(float))
content_size_bg_by_user = defaultdict(lambda:defaultdict(int))
content_energy_bg_by_user = defaultdict(lambda:defaultdict(float))

content_tail_energy_by_user = defaultdict(lambda:defaultdict(float))
content_active_energy_by_user = defaultdict(lambda:defaultdict(float))

if by_flow:
    flows = c_session.CFlow()
    flows.load_data()
else:
    flows = c_session.CEnergy()
    flows.load_data()

timestamp_adjustor = 3600 * 24 # * 24 * 7
last_day = None
for item in flows.data:
    if by_flow:
        time = max(item["start_time"], item["tmp_start_time"])
        timestamp = int(time/timestamp_adjustor)
        energy = item["active_energy"] + item["passive_energy"]
        data =  item["total_dl_whole"] + item["total_ul_whole"]
        userid = item["userID"]

        fg_log = item["fg_log"]
        fg_code = -1
        if len(fg_log) > 0:
            fg_log.sort(key=operator.itemgetter(1))
            fg_code = fg_log[0][0]

        if fg_code == 400 or fg_code == 130 or fg_code == 300:
            content_size_bg_by_user[timestamp][userid] += data
            content_energy_bg_by_user[timestamp][userid] += energy
    else:
        userid = item["userid"]
        timestamp = int(item["timestamp"])/timestamp_adjustor
        energy = item["energy"]
        data = item["upbytes"] + item["downbytes"]

    if last_day != timestamp:
        print timestamp

    content_size_by_user[timestamp][userid] += data
    content_energy_by_user[timestamp][userid] += energy
    content_tail_energy_by_user[timestamp][userid] += item["passive_energy"] 
    content_active_energy_by_user[timestamp][userid] += item["active_energy"]
    last_day = timestamp

times = content_size_by_user.keys()
times.sort()

if by_flow:
    f = open("output_files/longitudinal_all.txt", "w")
else:
    f = open("output_files/longitudinal_all_total.txt", "w")

for t in times:
    for k, v in content_size_by_user[t].iteritems():
        if by_flow:
            print >>f, t, k, v, content_energy_by_user[t][k], content_size_bg_by_user[t][k], content_energy_bg_by_user[t][k], content_tail_energy_by_user[t][k], content_active_energy_by_user[t][k]
        else:
            print >>f, t, k, v, content_energy_by_user[t][k]
f.close() 
