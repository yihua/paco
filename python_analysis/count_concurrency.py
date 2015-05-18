#!/usr/bin/python

import c_session
import sys
import operator
import numpy

from collections import defaultdict

user_foreground = defaultdict(lambda:defaultdict(int))
user_background = defaultdict(lambda:defaultdict(int))

passive_energy_front = []
passive_energy_back = []


flows = c_session.CFlow()
flows.load_data()

for item in flows.data:
    time = max(item["start_time"], item["tmp_start_time"])
    end_time = max(item["last_ul_pl_time"], item["last_dl_pl_time"])

    passive_energy =  item["passive_energy"]
    cell = item["network_type"] 
    userid = item["userID"]

    fg_log = item["fg_log"]
    foreground = False
    for item in fg_log:
        if item[0] == 100 or item[0] == 200:
            foreground = True
            break

    if foreground:
        for i in range(int(time), int(end_time) + 1):
            user_foreground[userid][i] += 1
        if cell == 1:
            passive_energy_front.append(passive_energy)

    else:
        for i in range(int(time), int(end_time) + 1):
            user_background[userid][i] += 1
        if cell == 1:
            passive_energy_back.append(passive_energy)

concurrency_fg = defaultdict(int)
concurrency_bg = defaultdict(int)

total_fg = 0
total_bg = 0

users = set(user_foreground.keys()) | set(user_background.keys())
for user in users:
    times = set(user_foreground[user].keys()) | set(user_background[user].keys())
    for t in times:
        if user in user_foreground and t in user_foreground[user] and user_foreground[user][t] >0:
            concurrent = user_foreground[user][t] + user_background[user][t]
            concurrency_fg[concurrent] += 1
            total_fg += 1

        elif user in user_background and t in user_background[user] and user_background[user][t] >0:
            concurrent = user_background[user][t]
            concurrency_bg[concurrent] += 1
            total_bg += 1

print "tail energy, front", numpy.mean(passive_energy_front)
print "tail energy, back", numpy.mean(passive_energy_back)
   
print
for k, v in concurrency_fg.iteritems():
    print k, v/float(total_fg)
print
for k, v in concurrency_bg.iteritems():
    print k, v/float(total_bg)

