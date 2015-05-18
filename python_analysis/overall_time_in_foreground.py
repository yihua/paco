#!/usr/bin/python

from collections import defaultdict

import operator

import glob
import numpy

dirs = ["/nfs/beirut2/ashnik/active_data/active_sorted_201210", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201212", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201301", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201302", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201303", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201304", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201305", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201306", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201307", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201308", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201309", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201310", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201311", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201312", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201401", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201402", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201403", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201404", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201405", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201406", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201407", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201408"]

user_last_time = defaultdict(int)
last_time_nums = defaultdict(lambda:False)

user_foreground_times = defaultdict(lambda:defaultdict(int))
user_background_times = defaultdict(lambda:defaultdict(int))

for name in dirs:
    f = open(name)
    print name
    for line in f:
        (imei, time, appname, is_foreground) = line.split()
        is_foreground = (is_foreground == "100" or is_foreground =="200")
        time = int(time)
        if user_last_time[imei] != time and user_last_time[imei] != 0:

            week = user_last_time[imei]/(3600*1000*24*7)

            if last_time_nums[imei]:
                user_background_times[week][imei] += time - user_last_time[imei]
            else:
                user_foreground_times[week][imei] += time - user_last_time[imei]

            last_time_nums[imei] = False 
        if is_foreground:
            last_time_nums[imei] = True
    user_last_time[imei] = time

times = set(user_background_times.keys())
times = list(times)
times.sort()

for t in times:
    for u, bg in user_background_times[t].iteritems():
        if t in user_foreground_times and u in user_foreground_times[t]:
            fg = user_foreground_times[t][u]
        else:
            fg = 0
        print t, u, bg, fg
