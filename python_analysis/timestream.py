#!/usr/bin/python

import operator
import c_session 
import glob
import sys
import zipfile
import json

# This is for merging attributes with a trace (rather than an hour-by-hour timeline; we 
# convert to such a timeline after)
#
#     Right now I'm sort of assuming each thing sent can be treated as more
#     or less one point in time, this may be an unreasonable approximation eventually.
#
#  Format of timeline data:
#     dict: [time][other data structure]
#
#  Format of other data:
#     list: [begin_time, end_time, data] 
#     list hsould be non-overlapping
#
#  Output:
#     A valid timeline to which more data can be added
#
#  Treat each user separately

def load_from_file(glob_strings, file_name, parse_function, generate_attributes, add_attribute, limit = -1):

    # list of all locs ordered by time
    user_attributes = {}

    # pending location to finish, optional
    user_attribute_rating = {}

    # Determine unique locations and the times the user is there
    user_last_attribute = {}

    # optional
    user_top_attributes = {}
    
    dirs = []
    for glob_string in glob_strings:
        dirs.extend(glob.glob(glob_string))

    dirs.sort() # XXX
    for d in dirs:
        if limit != -1:
            if limit== 0:
                break
            limit -= 1

        user = d.split("/")[-2].split("-")[-1]

        if user not in user_attributes:
            user_attributes[user] = []
            user_attribute_rating[user] = {}

        try:
            archive = zipfile.ZipFile(d, 'r')
        except:
            print "warning! not a zip file?", d
            print sys.exc_info()[0]
            continue

        last_attr = None
        if user in user_last_attribute:
            last_attr = user_last_attribute[user]
            
        with archive.open(file_name) as f:
            for line in f:
                retval = parse_function(user_attributes, user_attribute_rating, last_attr, line, user)
                if retval != None:
                    (user_attributes, user_attribute_rating, last_attr) = retval
        user_last_attribute[user] = last_attr

    (user_attributes, user_attribute_rating, user_top_attributes) = \
            generate_attributes(user_attributes, user_attribute_rating, user_top_attributes)

    timestream = {}
    for user, timeline in user_attributes.iteritems():
        if len(timeline) == 0:
            continue
        timestream[user] = [] 

        for attribute in timeline:
            timestream = add_attribute(user, timestream, attribute, user_top_attributes)
        timestream[user].sort(key=operator.attrgetter("begin_time"))
    return timestream

class AttributeItem:
    def __init__(self, user=None, begin_time=None, end_time=None, other_data=None):
        """
        Data to merge with the timeline

        user: same userid we use for everything else
        begin_time: beginning of the time the attribute is valid
        end_time: end of the time the attribute is valid
        other_data: dict of other data to merge, please prepend with a unique string for the module to avoid overlap
        """

        if user != None:
            self.user = user
            self.begin_time = int(begin_time)
            self.end_time = int(end_time)
            self.other_data = other_data

#        l.sort(key=operator.attrgetter("begin_time"))

    def to_string(self):
        return json.dumps({"user":self.user, "begin_time": self.begin_time, \
                "end_time": self.end_time, "other_data": self.other_data}) 

    def from_string(self, string):
        data = json.loads(string)
        self.user = data["user"]
        self.begin_time = data["begin_time"]
        self.end_time = data["end_time"]
        self.other_data = data["other_data"]

    def merge_timeline_item(self, timeline_item):
        for k, v in timeline_item.data.iteritems():
            if k not in self.other_data:
                self.other_data[k] = []
            self.other_data[k].append(v)
    
    def match_attribute(self, attribute):
        """
        Return -1 if smaller, 0 if the same size, 1 if bigger
        """
        if self.begin_time < attribute.begin_time:
            return -1
        if self.begin_time > attribute.end_time:
            return 1
        else:
            return 0

class TimestreamItem:

    def __init__(self, user, time, time_end, data_start_attributes):
        """data_start_attributes: a dict of labels and values
        """
        self.user = user
        self.begin_time = int(float(time)*1000)
        self.time_end = int(float(time_end)*1000) # We ignore this in most cases as an approximation...
        self.data = data_start_attributes 

    def merge_attribute(self, attribute, overwrite=False):
        """ 
        Merge an attribute item with the timestream item, no checks

        attribute: a AttributeItem object 
        """

        assert(attribute.user == self.user)
        for k, v in attribute.other_data.iteritems():
            if not overwrite and k in self.data:
                print "WARNING! OVEWRITITNG ", k
            self.data[k] = v

    def match_attribute(self, attribute):
        """
        Return -1 if smaller, 0 if the same size, 1 if bigger
        """
        if self.begin_time < attribute.begin_time:
            return -1
        if self.begin_time > attribute.end_time:
            return 1
        else:
            return 0

def merge(timestream_list, attribute_list, reverse=False):
    """ Assign the appropriate attribute to the timestream.

    If reverse is false, assign the network data to the attribute instead.
    
    Both must be sorted."""

    # I'm sure there's a more pythonic way of doing this...
    attribute_list_ptr = 0
    attribute_list_last = len(attribute_list)
    for item in timestream_list:

        if attribute_list_ptr >= attribute_list_last:
            break

        
        while   attribute_list_ptr < attribute_list_last and \
                item.match_attribute(attribute_list[attribute_list_ptr]) > 0:
#            print "not yet...", attribute_list[attribute_list_ptr].begin_time, item.time
            attribute_list_ptr += 1
#        print "maybe...", attribute_list[attribute_list_ptr].begin_time, item.time

        if  attribute_list_ptr < attribute_list_last and \
                item.match_attribute(attribute_list[attribute_list_ptr]) == 0:
            if not reverse:
                item.merge_attribute(attribute_list[attribute_list_ptr])
            else:
#                print "merging!", attribute_list[attribute_list_ptr].begin_time, item.time
                attribute_list[attribute_list_ptr].merge_timeline_item(item)

def load_timeline(limit=-1):
    flows = c_session.CFlow()
    flows.load_data(limit)

    timeline = {} 
    for item in flows.data:
        user = item["userID"]
        time = max(item["start_time"], item["tmp_start_time"])
        end_time = max(item["last_ul_pl_time"], item["last_dl_pl_time"])
        data_start_attributes = {}
        data_start_attributes["flow_host"] = item["app_name"].split(":")[0]
        data_start_attributes["total_dl_whole"] = item["total_dl_whole"] 
        data_start_attributes["total_ul_whole"] = item["total_ul_whole"] 
        data_start_attributes["flow_content"] = item["content_type"] 
        data_start_attributes["flow_encrypted"] = (len(item["host"]) == 0)
        data_start_attributes["is_wifi"] = (item["network_type"] == 0) 
        data_start_attributes["active_energy"] = item["active_energy"]
        data_start_attributes["passive_energy"] =  item["passive_energy"]
        data_start_attributes["app_name"] =  item["app_name"].split(":")[0]
        data_start_attributes["content_type"] = item["content_type"]
        data_start_attributes["request_url"] = item["request_url"]
        data_start_attributes["timestamp_log"] = item["timestamp_log"]
        data_start_attributes["energy_log"] = item["energy_log"]
        data_start_attributes["fg_log"] = item["fg_log"]
        data_start_attributes["content_length"] = item["content_length"]

#        if "facebook" in item["app_name"]:
#            print "energy:", time, item["active_energy"], item["passive_energy"], item["total_dl_payload_h"], item["total_ul_payload_h"]

        if user not in timeline:
            timeline[user] = []
        timeline[user].append(TimestreamItem(user, time, end_time, data_start_attributes))

    for user, user_timeline in timeline.iteritems():
        user_timeline.sort(key=operator.attrgetter("begin_time"))
    return timeline

if __name__ == "__main__":

    user_gps = []
    user_flow = []

#    for i in range(10):
#        other_data = {"test_data":i}
#        user_gps.append(AttributeItem( "me", 20 + i*5, 40 + i*5, other_data))
#        other_data_attributes = {"test_data_2":i*2}
#        user_flow.append(TimestreamItem("me", i*0.01, i*0.01+5, other_data_attributes))

    other_data = {"test_data":"a"}
    user_gps.append(AttributeItem( "me", 5*1000, 10*1000, other_data))
    other_data = {"test_data":"b"}
    user_gps.append(AttributeItem( "me", 15*1000, 20*1000, other_data))
    other_data = {"test_data":"c"}
    user_gps.append(AttributeItem( "me", 25*1000, 30*1000, other_data))
    other_data = {"test_data":"d"}
    user_gps.append(AttributeItem( "me", 35*1000, 40*1000, other_data))

    other_data_attributes = {"test_data_2":"in"}
    user_flow.append(TimestreamItem("me", 12, 21, other_data_attributes))
    other_data_attributes = {"test_data_2":"in"}
    user_flow.append(TimestreamItem("me", 15, 18, other_data_attributes))
    other_data_attributes = {"test_data_2":"in2"}
    user_flow.append(TimestreamItem("me", 19, 20, other_data_attributes))

    merge(user_flow, user_gps, reverse=True)

    for item in user_gps:
        print item.user, item.begin_time, item.end_time, item.other_data
#    for item in user_flow:
#        print item.user, item.time, item.time_end, item.data
