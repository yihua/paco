#!/usr/bin/python

import c_session
import operator
from collections import defaultdict

# Organize by user, then by app

CUTOFF = 0.6
DATA_POINTS_NEEDED = 5 
class PeriodicData:
    def __init__(self, item):

        self.time = int(max(item["start_time"], item["tmp_start_time"]))
        self.data = item["total_dl_payload_h"] + item["total_ul_payload_h"]
        self.active_energy = item["active_energy"] 
        self.passive_energy = item["passive_energy"] 
        self.app_name = item["app_name"].split(":")[0]
        self.host_name = set(item["host"])

    def merge(self, data):
        if data.time != self.time:
            return
        assert(data.app_name == self.app_name)

        self.data += data.data
        self.active_energy += data.active_energy
        self.passive_energy += data.passive_energy
        self.host_name.update(data.host_name)

    def printme(self, f):
        print >>f, "\t", self.host_name, self.data, self.active_energy, self.passive_energy


def get_data_validate():
    #users = ["a", "b", "c"]
    users = ["a"]
    #appnames = ["x", "y", "z"]
    appnames = ["x"]

    timeline = {}

    for user in users:
        timeline[user] = {}
        for appname in appnames:
            timeline[user][appname] = {}
            for i in range(0, 1000, 10):
                timeline[user][appname][i] = None

    return timeline

def get_data(appname_filter=[], limit=-1):
    flows = c_session.CFlow()
    flows.load_data(limit)

    timeline = {} 
    for item in flows.data:

        user = item["userID"] + item["clt_ip_tuple"][0] + \
                item["clt_ip_tuple"][1] + item["server_ip_tuple"][0] + \
                item["server_ip_tuple"][1]
        flow_appname = item["app_name"].split(":")[0]
        if appname_filter and  flow_appname not in appname_filter:
            continue

        data = PeriodicData(item)
        time = data.time
        appname = data.app_name

        if user not in timeline:
            timeline[user] = {}
        if flow_appname not in timeline[user]:
            timeline[user][appname] = {}

        if time in timeline[user][appname]:
            timeline[user][appname][time].merge(data)
        else:
            #print time, data.time
            timeline[user][appname][time] = data 

    return timeline

def detect_periodicity(timeline_user_app, user, appname, candidate_periods, candidate_other_data, candidate_requests, rounding=1, upper=60):
    """
    Input of this function = output of get_data[user][appname]
    """

    timeline = {}
    for k, v in timeline_user_app.iteritems():
        t = k / rounding
        if t in timeline:
            timeline[t].merge(v)
        else:
            timeline[t] = v

    min_val = min(timeline.keys())
    max_val = max(timeline.keys())
    range_steps = upper / rounding

    range_counter = [[0 for j in range(i)] for i in range (2,range_steps)]
    total_counter = [[0 for j in range(i)] for i in range (2,range_steps)]

    items = [[[] for j in range(i)] for i in range (2,range_steps)]
   
#    for item in range_counter:
#        print item

    # Count periodic data
    for i in range(min_val, max_val):
        for j in range(2,range_steps):
            time_offset = i % j
            period_index = j - 2
            total_counter[period_index][time_offset] += 1
            if i in timeline:
                range_counter[period_index][time_offset] += 1
                items[period_index][time_offset].append(timeline[i])


    for i in range(2,range_steps):
        for j in range(len(range_counter[i-2])):
            if range_counter[i-2][j] > DATA_POINTS_NEEDED:# and \
                    candidate_periods[i] += range_counter[i-2][j]
                    candidate_other_data[i] += total_counter[i-2][j]
                    candidate_requests[i].append(items[i-2][j])


def evaluate_periodicity(candidate_periods, candidate_other_data, candidates_request, appname, f):
    candidates_to_sort = {}
    for k, v in candidate_periods.iteritems():
        if v > 2:
            candidates_to_sort[k] = v/float(candidate_other_data[k])

    candidates = sorted(candidates_to_sort.items(), key=operator.itemgetter(1), reverse=True)

    for i in range(min(len(candidates),60)):
        val = candidates[i][1]
        key = candidates[i][0]
        print >>f,  appname, "period of", key, "data points", val, candidate_periods[key], candidate_other_data[key]

        if i == 0:
            for item in candidates_reqest:
                item.printme(f)
                

# Deprecated
def format_data_fft(test_data):
    data = []
    max_val = max(test_data.keys())
    min_val = min(test_data.keys())
    for i in range(min_val, max_val):
        if i in test_data:
            data.append(test_data[i])
        else:
            data.append(0)

    sp = numpy.fft.fft(data)
    freq = numpy.fft.fftfreq(len(data))
    for f in frequency:
        print f / 5

if __name__ == "__main__":

    test_hosts = []
    f = open("output_files/top_total_hosts.txt")
    limit = 25 
    for line in f:
        line = line.split()[0]
        test_hosts.append(line)
        limit -= 1
        if limit == 0:
            break
    f.close()

#    timeline = get_data(test_hosts, 100000)
    timeline = get_data(test_hosts)
    #timeline = get_data_validate()

    # Evaluate periodic data
    candidate_periods_min = defaultdict(lambda: defaultdict(int))
    candidate_other_data_min = defaultdict(lambda:defaultdict(int))
    candidate_requests_min = defaultdict(lambda:defaultdict(int))
    candidate_periods_hour = defaultdict(lambda: defaultdict(int))
    candidate_other_data_hour = defaultdict(lambda:defaultdict(int))
    candidate_requests_hour= defaultdict(lambda:defaultdict(int))

    for user, applist in timeline.iteritems():
        for appname, flow in applist.iteritems():
            detect_periodicity(flow, user, appname, candidate_periods_min[appname], candidate_other_data_min[appname], candidate_requests_min[appname], 5, 120)
            detect_periodicity(flow, user, appname, candidate_periods_hour[appname], candidate_other_data_hour[appname], candidate_requests_min[appname], 60, 4000)

    f = open("output_files/find_periodic.txt", "w")

    print >>f, "by five minutes..."
    for appname, candidate_period in candidate_periods_min.iteritems():
        print >>f
        evaluate_periodicity(candidate_period, candidate_other_data_min[appname], candidate_requests_min[appname], appname, f)
    print >>f, "by hour..."
    for appname, candidate_period in candidate_periods_hour.iteritems():
        print >>f
        evaluate_periodicity(candidate_period, candidate_other_data_hour[appname], candidate_requests_hour[appname], appname, f)

