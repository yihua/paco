#!/usr/bin/python

import timestream
import timeline
import glob
import zipfile
import operator
import c_session

class GpsAttribute(timestream.AttributeItem):
    def __init__(self, user, begin_time, end_time, location_code):

        other_data = {"loc_index" : location_code}
        timestream.AttributeItem.__init__(self, user, begin_time, end_time, other_data)


def parse_function(user_locs, user_loc_rating, last_loc, line, user):
    if "LOCATION" not in line:
        return None
    line = line.split()
    if len(line) > 7:
        return None 
    gps = line[-1]
    gps = gps[1:-1]
    (lat, lng) = gps.split(",")
    lat = str(int(float(lat[:5]) * 200)/200.0)
    lng = str(int(float(lng[:6]) * 200)/200.0)
    time = line[0]

#    print "LOCATION DATA:", line
    if last_loc != None:
        if last_loc[1] != lat or last_loc[2] != lng:
            last_loc.append(time)
            user_locs[user].append(last_loc)
            
            loc_code = last_loc[1] + "|" + last_loc[2]
            if loc_code not in user_loc_rating[user]:
                user_loc_rating[user][loc_code] = 0 
            user_loc_rating[user][loc_code] += int(time) - int(last_loc[0])

            last_loc = [time, lat, lng]

    else:
        last_loc = [time, lat, lng]

    return (user_locs, user_loc_rating, last_loc)



def generate_attributes(user_locs, user_loc_rating, user_top_locs):
    
    # Find the top 3 locations + all others

    user_top_locs = {}
    for user, loc_rating in user_loc_rating.iteritems():
        loc_sorted = sorted(loc_rating.items(), key=operator.itemgetter(1), reverse=True)     
        user_top_locs[user] = []
        print "-------------------------"
        print user
        for i in range(min(5, len(loc_sorted))):
            print "top loc", loc_sorted[i]
            user_top_locs[user].append(loc_sorted[i][0]) 
    return (user_locs, user_loc_rating, user_top_locs)

def add_attribute(user, loc_timestream, loc, user_top_locs):
    loc_code = loc[1] + "|" + loc[2]

    loc_number = 10 
    if loc_code in user_top_locs[user]:
        loc_number = user_top_locs[user].index(loc_code)
        
    loc_timestream[user].append(GpsAttribute(user, loc[0], loc[-1], loc_number))

    return loc_timestream

def load_by_user(limit =-1):
    #glob_string = "/nfs/beirut1/userstudy/2nd_round/201303/**/psmn-2013-03-*/device_info.zip"
    glob_strings = ["/nfs/beirut1/userstudy/2nd_round/*/psmn-20*/device_info.zip", "/nfs/beirut1/userstudy/2nd_round/*/*/psmn-20*/device_info.zip"]
    file_name = "device_info"
    return timestream.load_from_file(glob_strings, file_name, parse_function, generate_attributes, add_attribute, limit)

def save_to_file(loc_timeline, filename):
    f = open(filename, "w")
    for user, item in loc_timeline.iteritems():
        print >>f, item.to_string()

def load_from_file(filename):
    timestream = {}
    f = open(filename)
    for line in f.readlines():
        new_item = AttributeItem()
        new_item.from_string(line)
        timestream[new_item.user] = new_item
    return timestream
    


if __name__ == "__main__":

    gps_timeline = load_by_user()

    print "==================================="

    timestamp_adjustor = 3600 * 24 * 7
    tl = timeline.TimeLine("data_by_hour_gps")
    flow_timeline = timestream.load_timeline()

    for user, user_flow in flow_timeline.iteritems():
        if user not in gps_timeline:
            continue
        user_gps = gps_timeline[user]

        timestream.merge(user_flow, user_gps)
        for item in user_flow:

            if "loc_index" in item.data:
                loc_index = item.data["loc_index"]
            else:
                loc_index = -1

            up_data = item.data["flow_ul_payload"]
            down_data = item.data["flow_dl_payload"]
            up_data_encr = 0
            down_data_encr = 0
            if item.data["flow_encrypted"]:
                up_data_encr = up_data
                down_data_encr = down_data
                up_data = 0
                down_data = 0
                
            tl.add_data_point(item.time, item.user, item.data["flow_host"], loc_index, -1, item.data["flow_content"], up_data, down_data, up_data_encr, down_data_encr, timestamp_adjustor)

    tl.sync_to_database()
    tl.generate_plot(["location_rating"])

