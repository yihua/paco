#!/usr/bin/python

import c_session
import sys
import operator
from collections import defaultdict

flows = c_session.CFlow()
flows.load_data()
flows.data.sort(key=lambda k: max(k["start_time"], k["tmp_start_time"]))

last_time = defaultdict(int)
for item in flows.data:
    userid = item["userID"]

    time = max(item["start_time"], item["tmp_start_time"])
    if "com.sec.spp.push" not in item["app_name"]:
        last_time[userid] = time
        continue

    time_since_last_active = -1
    if userid in last_time:
        time_since_last_active = time - last_time[userid]

    
    delta_time = max(item["last_ul_pl_time"], item["last_dl_pl_time"]) - time

    if delta_time < 0:
        delta_time = 0

    down_size = item["total_dl_whole"]
    up_size = item["total_ul_whole"]
    cell = item["network_type"] 
    active_energy  = item["active_energy"]
    passive_energy =  item["passive_energy"]

    fg_log = item["fg_log"]

    fg_code = -1

    if len(fg_log) > 0:
        fg_log.sort(key=operator.itemgetter(1))
        fg_code = fg_log[0][0]

    print time, userid, delta_time, down_size, up_size, cell, active_energy, passive_energy, fg_code, 0, "none", "none", "none", time_since_last_active

    # timestamp, userid, size, energy, foreground, background 


