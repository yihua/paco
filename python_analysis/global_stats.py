#!/usr/bin/python
import c_session
import operator


all_active = 0
all_passive = 0

all_foreground = 0
all_background = 0
all_perceptible = 0
all_service = 0

all_foreground_data = 0
all_background_data = 0
all_perceptible_data = 0
all_service_data = 0

flows = c_session.CFlow()
flows.load_data(-1)

for item in flows.data:
    all_active += item["active_energy"]
    all_passive += item["passive_energy"]
    
    fg_code = -1
    fg_log = item["fg_log"]

    if len(fg_log) > 0:
        fg_log.sort(key=operator.itemgetter(1))
        fg_code = fg_log[0][0]

    if fg_code == 100 or fg_code == 200:
        all_foreground += item["active_energy"] + item["passive_energy"]
        all_foreground_data += item["total_dl_whole"] +  item["total_ul_whole"]
    elif fg_code == 130:
        all_perceptible += item["active_energy"] + item["passive_energy"]
        all_perceptible_data += item["total_dl_whole"] +  item["total_ul_whole"]
    elif fg_code == 300:
        all_service_data += item["total_dl_whole"] +  item["total_ul_whole"]
        all_service += item["active_energy"] + item["passive_energy"]

    elif fg_code == 400:
        all_background_data += item["total_dl_whole"] +  item["total_ul_whole"]
        all_background += item["active_energy"] + item["passive_energy"]


print all_active, all_passive
print all_foreground, all_background, all_perceptible, all_service
print all_foreground_data, all_background_data, all_perceptible_data, all_service_data
