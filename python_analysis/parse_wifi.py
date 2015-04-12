#!/usr/bin/python

import timeline
import timestream
import glob
import zipfile
import operator
import c_session

class NetworkTypeAttribute(timestream.AttributeItem):
    def __init__(self, user, begin_time, end_time, location_code, network_location):

        other_data = {"network_type" : location_code, "network_location": network_location}
        timestream.AttributeItem.__init__(self, user, begin_time, end_time, other_data)

def parse_function(user_wifi, user_wifi_rating, last_wifi, line, user):
    data_type = None
    location_type = None
    if "CELL LOCATION CHANGED" in line:
        data_type = "cell"
    elif "WIFI CONNECTED" in line:
        data_type = "wifi"
    else:
        return None 

    line = line.split()
    time = line[0]

    if data_type == "wifi":
        if line[6] == "MWireless":
            location_type = "CSE"
        else:
            location_type = "home_wifi"
    else:
        location_type = "neither"
    

    if last_wifi != None:
        if last_wifi[1] != data_type or last_wifi[2] != location_type:
            last_wifi.append(time)
            user_wifi[user].append(last_wifi)
            last_wifi = [time, data_type, location_type]
    else:
        last_wifi = [time, data_type, location_type]
    return (user_wifi, user_wifi_rating, last_wifi)

def load_by_user(limit=-1):
    glob_string = ["/nfs/beirut1/userstudy/2nd_round/*/psmn-20*/network_details.zip", "/nfs/beirut1/userstudy/2nd_round/*/*/psmn-20*/network_details.zip"]
    file_name = "network_details"
    return timestream.load_from_file(glob_string, file_name, parse_function, generate_attributes, add_attribute, limit)

# 1377977735407   CELL LOCATION CHANGED   36655317    31991   0
# [1375798012353] CONNECTED 2 -200 08:1f:f3:b2:35:72 "MWireless" -1 -1614495165 5c:0a:5b:1a:c9:fb
# 1407179250768WIFI CONNECTED6-6700:26:cb:18:6a:60MWireless65-6722677415C:0A:5B:F8:BD:A3


def generate_attributes(user_wifi, user_wifi_rating, user_top_wifi):
    return (user_wifi, user_wifi_rating, user_top_wifi)

def add_attribute(user, wifi_timestream, wifi, user_top_wifi):
    wifi_timestream[user].append(NetworkTypeAttribute(user, wifi[0], wifi[-1], wifi[1], wifi[2]))
#    print "Wifi attributes", user, wifi[0], wifi[-1], wifi[1], wifi[2]
    return wifi_timestream


if __name__ == "__main__":

    wifi_timeline = load_by_user()

    timestamp_adjustor = 3600 * 24 * 7
    tl  = timeline.TimeLine("data_by_hour_wifi")
    flow_timeline = timestream.load_timeline()

    total_cellular = 0
    total_mwireless = 0
    total_other_wireless = 0

    total_cellular_up = 0
    total_mwireless_up = 0
    total_other_wireless_up = 0

    for user, user_flow in flow_timeline.iteritems():
        if user not in wifi_timeline:
            continue
        user_wifi = wifi_timeline[user]

        timestream.merge(user_flow, user_wifi)

        for item in user_flow:
            if "network_location" not in item.data:
                continue

            loc = item.data["network_location"]
            up_data = item.data["flow_ul_payload"]
            down_data = item.data["flow_dl_payload"]
            up_data_encr = 0
            down_data_encr = 0
            if item.data["flow_encrypted"]:
                up_data_encr = up_data
                down_data_encr = down_data
                up_data = 0
                down_data = 0

            print "data point added:", item.time, item.user, loc

            if loc == "CSE":
                loc = 1
                total_mwireless += down_data + down_data_encr
                total_mwireless_up += up_data + up_data_encr
            elif loc == "home_wifi":
                total_other_wireless += down_data + down_data_encr
                total_other_wireless_up += up_data + up_data_encr
                loc = 2
            elif loc == "neither":
                total_cellular += down_data + down_data_encr
                total_cellular_up += up_data + up_data_encr
                loc = 3

            tl.add_data_point(item.time, item.user, item.data["flow_host"], loc, -1, item.data["flow_content"], up_data, down_data, up_data_encr, down_data_encr, timestamp_adjustor)
    tl.sync_to_database()
    tl.generate_plot(["location_rating"])

    print "TOTAL:", total_mwireless, total_mwireless_up, total_other_wireless, total_other_wireless_up, total_cellular, total_cellular_up
