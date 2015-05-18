#/usr/bin/python

import c_session
import sys
import operator

app_to_examine = "com.sec.spp.push"
#app_to_examine = "com.twitter.android"
#app_to_examine = "com.sina.weibo.servant"
if len(sys.argv) > 1:
    app_to_examine = sys.argv[1]
flows = c_session.CFlow()
flows.load_data(-1, app_to_examine)

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

    userid = item["userID"]
    fg_log = item["fg_log"]

    fg_code = -1

    if len(fg_log) > 0:
        fg_log.sort(key=operator.itemgetter(1))
        fg_code = fg_log[0][0]

    if len(item["content_type"]) > 1:
        host = item["host"]
        energy_list = item["energy_log"]
        sizes = item["content_length"]
        content_type = item["content_type"]
        request_url = item["request_url"]
        timestamp_log = item["timestamp_log"]

        for i in range(len(content_type)):
            try:

                (start_t, end_t) = timestamp_log[i].split(",")

                fg_code = -1
                for item in fg_log:
                    if item[1] <= start_t and item[2] <= start_t:
                        fg_code = item[0]
                        break

                delta_t = float(end_t) - float(start_t) 

                local_active_energy, local_passive_energy = energy_list[i].split(",")

                print time, userid, delta_t, sizes[i], 0, cell, float(local_active_energy), float(local_passive_energy), fg_code, 1, content_type[i], host[i], request_url[i] 
            except:
                continue

    print time, userid, delta_time, down_size, up_size, cell, active_energy, passive_energy, fg_code, 0, "none", "none", "none"

    # timestamp, userid, size, energy, foreground, background 


