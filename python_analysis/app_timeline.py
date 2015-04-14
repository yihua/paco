#/usr/bin/python

import c_session
import sys

app_to_examine = "com.sec.spp.push"
#app_to_examine = "com.twitter.android"
#app_to_examine = "com.sina.weibo.servant"
if len(sys.argv) > 1:
    app_to_examine = sys.argv[1]
flows = c_session.CFlow()
flows.load_data()

for item in flows.data:

#    print item["fg_log"]
    if app_to_examine not in item["app_name"]:
        continue
    
    time = max(item["start_time"], item["tmp_start_time"])
    delta_time = max(item["last_ul_pl_time"], item["last_dl_pl_time"]) - time

    if delta_time < 0:
        delta_time = 0

    down_size = item["total_dl_whole"]
    up_size = item["total_ul_whole"]
    cell = item["network_type"] 
    active_energy  = item["active_energy"]
    passive_energy =  item["passive_energy"]
    content_type = item["content_type"]
    request_url = item["request_url"]
    host = item["host"]
    userid = item["userID"]

    foreground = len(item["fg_log"][0]) > 0 

    print time, userid, delta_time, down_size, up_size, cell, active_energy, passive_energy, foreground, content_type, host, request_url 

    # timestamp, userid, size, energy, foreground, background 


