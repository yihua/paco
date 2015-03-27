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

def load_by_user(limit =-1):
    # list of all locs ordered by time
    user_locs = {}

    # pending location to finish
    user_last_loc = {}

    # figure out top n locs for each user
    user_loc_rating = {}

    dirs = glob.glob("/nfs/beirut1/userstudy/2nd_round/**/psmn-20*/device_info.zip")
#    dirs.extend(glob.glob("/nfs/beirut1/userstudy/2nd_round/**/psmn-20*/device_info.zip"))
    dirs.sort()

    # Determine unique locations and the times the user is there
    for d in dirs:
#        print d
        if limit != -1:
            if limit== 0:
                break
            limit -= 1


        user = d.split("/")[-2].split("-")[-1]
        if user not in user_locs:
            user_locs[user] = []
            user_loc_rating[user] = {} 

        try:
            archive = zipfile.ZipFile(d, 'r')
        except:
            print "warning! not a zip file?", d
            continue

        last_loc = None
        if user in user_last_loc:
            last_loc = user_last_loc[user]

        with archive.open("device_info") as f:
            for line in f:
#        for line in archive.readline("device_info"):
                if "LOCATION" not in line:
                    continue
                line = line.split()
                if len(line) > 7:
                    continue
                gps = line[-1]
                gps = gps[1:-1]
                (lat, lng) = gps.split(",")
                lat = lat[:5]
                lng = lng[:6]
                time = line[0]

                if last_loc != None:
#                    print last_loc
                    if last_loc[1] != lat or last_loc[2] != lng:
                        last_loc.append(time)
                        user_locs[user].append(last_loc)
                        
                        loc_code = lat + "|" + lng
                        if loc_code not in user_loc_rating[user]:
                            user_loc_rating[user][loc_code] = 0
                        user_loc_rating[user][loc_code] += int(time) - int(last_loc[0])

                        last_loc = [time, lat, lng]

                else:
                    last_loc = [time, lat, lng]
            
        user_last_loc[user] = last_loc

    # Find the top 3 locations + all others

    user_top_locs = {}
    for user, loc_rating in user_loc_rating.iteritems():
        loc_sorted = sorted(loc_rating.items(), key=operator.itemgetter(1))     
        user_top_locs[user] = []
        for i in range(min(3, len(loc_sorted))):
            user_top_locs[user].append(loc_sorted[0]) 


    loc_timestream = {}
    f = open("user_loc_trends.txt", "w")
    for user, loc_timeline in user_locs.iteritems():
        if len(loc_timeline) == 0:
            continue
        loc_timestream[user] = []

        print loc_timeline
        for loc in loc_timeline:
            loc_code = loc[1] + "|" + loc[2]

            loc_number = 4
            if loc_code in user_loc_rating:
                loc_number = user_loc_rating.index(loc_code)
            
            print >>f, user, loc[0], loc[-1], loc_number

            loc_timestream[user].append(GpsAttribute(user, loc[0], loc[-1], loc_number))
        
    return loc_timestream

if __name__ == "__main__":

    gps_timeline = load_by_user()

#    exit()
    timestamp_adjustor = 3600 * 24
    timeline = timeline.TimeLine()
    flow_timeline = timestream.load_timeline()

    print "==================================="
    for user, user_flow in flow_timeline.iteritems():
        if user not in gps_timeline:
            continue
        user_gps = gps_timeline[user]

        timestream.merge(user_flow, user_gps)
        exit()
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

                
            timeline.add_data_point(item.time, item.user, item.data["flow_host"], loc_index, -1, item.data["flow_content"], up_data, down_data, up_data_encr, down_data_encr, timestamp_adjustor)

    timeline.sync_to_database()
    timeline.generate_plot(["location_rating"])

