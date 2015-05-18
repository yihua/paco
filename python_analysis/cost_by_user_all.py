#!/usr/bin/python

# DEPRECATED

import c_session
import sys
import operator
from collections import defaultdict

flows = c_session.CFlow()
flows.load_data()

user_energy = defaultdict(lambda: defaultdict(float))
user_sizes = defaultdict(lambda: defaultdict(int))

for item in flows.data:
    time = max(item["start_time"], item["tmp_start_time"])

    down_size = item["total_dl_whole"]
    up_size = item["total_ul_whole"]
    active_energy  = item["active_energy"]
    passive_energy =  item["passive_energy"]

    userid = item["userID"]

    week = int(time/(3600))
    user_sizes[week][userid] += (down_size + up_size)
    user_energy[week][userid] += (active_energy + passive_energy)

f = open("output_files/user_overhead_data_total.txt", "w")
for week, data in user_sizes.iteritems():
    for user, data2 in data.iteritems():
        print >>f, week, user, data2
f.close()

f = open("output_files/user_overhead_energy_total.txt", "w")
for week, data in user_energy.iteritems():
    for user, data2 in data.iteritems():
        print >>f, week, user, data2
f.close()

