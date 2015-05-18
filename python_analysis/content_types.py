#!/usr/bin/python
import c_session
import operator
import sys
import numpy
from collections import defaultdict

flows = c_session.CFlow()
flows.load_data()
timestamp_adjustor = 3600 * 24 * 7

interesting_content_types = ["image/jpg", "image/svg+xml", \
        "image/gif", "image/webp", "image/jpeg", "image/png", \
        "text/xml", "text/json", "text/html", "text/javascript", "video/3gpp", "video/mp4", "application/mpeg", "application/other", "video/other"]


f = open("content_types/all.txt", "w")
content_data = defaultdict(lambda:defaultdict(lambda:[[], [], []]))

for item in flows.data:

        content_types = item["content_type"]
        sizes = item["content_length"]
        energies = item["energy_log"]
        timestamps = item["timestamp_log"]
        is_wifi = (item["network_type"] == 0)

        for i in range(len(sizes)):
            try:
                energy_down, energy_up = energies[i].split(",")
                energy = float(energy_down) + float(energy_up)
                content_type = content_types[i]
                if content_type == "image/jpg":
                    content_type = "image/jpeg"
                elif content_type not in interesting_content_types and "application" in content_type:
                    content_type = "application/other"
                elif content_type not in interesting_content_types and "video" in content_type:
                    content_type = "video/other"
                size = int(sizes[i]) + item["total_ul_payload_h"]/len(sizes) + item["total_dl_payload_h"]/len(sizes)
            except:
                continue
            if size == 0:
                size = (item["total_ul_whole"] +  item["total_dl_whole"])/len(sizes)

            timestamp = int(float(timestamps[i].split(",")[0])/timestamp_adjustor)

            content_data[timestamp][content_type][0].append(size)
            content_data[timestamp][content_type][1].append(energy)
            if size > 0:
                content_data[timestamp][content_type][2].append(energy/float(size))

            content_data[timestamp]["all"][0].append(size)
            content_data[timestamp]["all"][1].append(energy)
            if size > 0:
                content_data[timestamp]["all"][2].append(energy/float(size))


        if len(sizes) == 0 and len(item["host"]) == 0:
            timestamp = int(float(item["start_time"])/timestamp_adjustor)
            size = item["total_dl_whole"] + item["total_ul_whole"]
            energy = item["active_energy"] + item["passive_energy"]
            content_data[timestamp]["encrypted"][0].append(size)
            content_data[timestamp]["encrypted"][1].append(energy)
            if size > 0:
                content_data[timestamp]["encrypted"][2].append(energy/float(size))
        else:
            timestamp = int(float(item["start_time"])/timestamp_adjustor)
            size = item["total_dl_whole"] + item["total_ul_whole"]
            energy = item["active_energy"] + item["passive_energy"]
            content_data[timestamp]["cleartext"][0].append(size)
            content_data[timestamp]["cleartext"][1].append(energy)
            if size > 0:
                content_data[timestamp]["cleartext"][2].append(energy/float(size))

for t, data in content_data.iteritems():
    print >>f, t,
    for content_type in interesting_content_types:

        if content_type in data and len(data[content_type][0]) > 10:
            print >>f, numpy.median(data[content_type][0]),  sum(data[content_type][0]), numpy.median(data[content_type][1]),  sum(data[content_type][1]), numpy.median(data[content_type][2]), sum(data[content_type][2]),len(data[content_type][0]),
        else:
            print >>f, "0 0 0 0 0 0 0 ",
    print >>f
f.close()

f = open("content_types/total.txt", "w")

for t, data in content_data.iteritems():
    print >>f, t, 
    if "all" in data and len(data["all"][0]) > 0:
        print >>f, numpy.median(data["all"][0]),  sum(data["all"][0]), numpy.median(data["all"][1]),  sum(data["all"][1]), numpy.median(data["all"][2]), sum(data["all"][2]),len(data["all"][0]),
    else:
        print >>f, "0 0 0 0 0 0 0 ",
    print >>f

f.close()

f = open("content_types/encrypted.txt", "w")

for t, data in content_data.iteritems():
    print >>f, t, 
    if "encrypted" in data and len(data["encrypted"][0]) > 0:
        print >>f, numpy.median(data["encrypted"][0]),  sum(data["encrypted"][0]), numpy.median(data["encrypted"][1]),  sum(data["encrypted"][1]), numpy.median(data["encrypted"][2]), sum(data["encrypted"][2]),len(data["encrypted"][0]),
    else:
        print >>f, "0 0 0 0 0 0 0 ",
    if "cleartext" in data and len(data["cleartext"][0]) > 0:
        print >>f, numpy.median(data["cleartext"][0]),  sum(data["cleartext"][0]), numpy.median(data["cleartext"][1]),  sum(data["cleartext"][1]), numpy.median(data["cleartext"][2]), sum(data["cleartext"][2]),len(data["cleartext"][0]),
    else:
        print >>f, "0 0 0 0 0 0 0 ",
    print >>f

f.close()
