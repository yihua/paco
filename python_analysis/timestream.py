#!/usr/bin/python

import operator

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

class TimestreamItem:
    def __init__(self, user, time, data_start_attributes):
        """

        data_start_attributes: a dict of labels and values
        """
        self.user = user
        self.time = time
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

def merge(timestream_list, attribute_list):
    """ Assign the appropriate attribute to the timestream"""

    attribute_list.sort(key=operator.attrgetter("begin_time"))
    timestream_list.sort(key=operator.attrgetter("time"))

    # I'm sure there's a more pythonic way of doing this...
    attribute_list_ptr = 0
    attribute_list_last = len(attribute_list)
    for item in timestream_list:

        if attribute_list_ptr >= attribute_list_last:
            break
        
        while item.match_attribute(attribute_list[attribute_list_ptr]) < 0 and \
                attribute_list_ptr < attribute_list_last:
            attribute_list_ptr += 1

        if item.match_attribute(attribute_list[attribute_list_ptr]) == 0:
            item.merge_attribute(attribute_list[attribute_list_ptr])

def load_timeline():
    flows = c_session.CFlow()
    flows.load_data()

    timeline = []
    for item in flows.data:
        user = item["userid"]
        time = item["start_time"] 
        data_start_attributes = {}
        data_start_attributes["flow_host"] = item["host"] 
        data_start_attributes["flow_dl_payload"] = item["total_dl_payload_h"] 
        data_start_attributes["flow_ul_payload"] = item["total_ul_payload_h"] 
        data_start_attributes["flow_content"] = item["content_type"] 
        timeline.append(TimestreamItem(user, time, data_start_attributes))

    return timeline
