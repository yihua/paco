#!/usr/bin/python

import operator
import c_session 

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

class AttributeItem:
    def __init__(self, user, begin_time, end_time, other_data):
        """
        Data to merge with the timeline

        user: same userid we use for everything else
        begin_time: beginning of the time the attribute is valid
        end_time: end of the time the attribute is valid
        other_data: dict of other data to merge, please prepend with a unique string for the module to avoid overlap
        """

        self.user = user
        self.begin_time = begin_time
        self.end_time = end_time
        self.other_data = other_data

    def sortme(self):
        attribute_list.sort(key=operator.attrgetter("begin_time"))

class TimestreamItem:
    def __init__(self, user, time, time_end, data_start_attributes):
        """

        data_start_attributes: a dict of labels and values
        """
        self.user = user
        self.time = time
        self.time_end = time_end # We ignore this in most cases as an approximation...
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

        if self.time < attribute.begin_time:
            return -1
        if self.time > attribute.end_time:
            return 1
        else:
            return 0

    def sortme(self):
        self.sort(key=operator.attrgetter("time"))

def merge(timestream_list, attribute_list):
    """ Assign the appropriate attribute to the timestream.
    
    Both must be sorted."""


    # I'm sure there's a more pythonic way of doing this...
    attribute_list_ptr = 0
    attribute_list_last = len(attribute_list)
#    print attribute_list
    for item in timestream_list:

        if attribute_list_ptr >= attribute_list_last:
            break
       


        while   attribute_list_ptr < attribute_list_last and \
                item.match_attribute(attribute_list[attribute_list_ptr]) < 0:
#            print "looking for attribute:", item.time, attribute_list[attribute_list_ptr].begin_time, attribute_list[attribute_list_ptr].end_time
            attribute_list_ptr += 1

        if  attribute_list_ptr < attribute_list_last and \
                item.match_attribute(attribute_list[attribute_list_ptr]) == 0:
            item.merge_attribute(attribute_list[attribute_list_ptr])

def load_timeline(limit=-1):
    flows = c_session.CFlow()
    flows.load_data(limit=-1)

    timeline = {} 
    for item in flows.data:
        user = item["userID"]
        time = max(item["start_time"], item["tmp_start_time"])
        end_time = max(item["last_ul_pl_time"], item["last_dl_pl_time"])
        data_start_attributes = {}
        data_start_attributes["flow_host"] = item["app_name"] 
        data_start_attributes["flow_dl_payload"] = item["total_dl_payload_h"] 
        data_start_attributes["flow_ul_payload"] = item["total_ul_payload_h"] 
        data_start_attributes["flow_content"] = item["content_type"] 
        data_start_attributes["flow_encrypted"] = (len(item["host"]) == 0)

        if user not in timeline:
            timeline[user] = []
        timeline[user].append(TimestreamItem(user, time, end_time, data_start_attributes))

    return timeline
