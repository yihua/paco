#!/usr/bin/python

import c_session

# Organize by user, then by app

CUTOFF = 0.6
DATA_POINTS_NEEDED = 100 
class PeriodicData:
    def __init__(self, item):

        self.time = int(max(item["start_time"], item["tmp_start_time"]))
        self.data = item["total_dl_payload_h"] + item["total_ul_payload_h"]
        self.active_energy = item["active_energy"] 
        self.passive_energy = item["passive_energy"] 
        self.app_name = item["app_name"]
        self.host_name = set(item["host"])

    def merge(self, data):
        if data.time != self.time:
            return
        assert(data.app_name == self.app_name)

        self.data += data.data
        self.active_energy += data.active_energy
        self.passive_energy += data.passive_energy
        self.host_name.update(data.host_name)

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

def get_data(limit=-1, appname_filter=[]):
    flows = c_session.CFlow()
    flows.load_data(limit)

    timeline = {} 
    for item in flows.data:

        user = item["userID"]
        if appname_filter and  item["app_name"] not in appname_filter:
            continue

        data = PeriodicData(item)
        time = data.time
        appname = data.app_name

        if user not in timeline:
            timeline[user] = {}
        if item["app_name"] not in timeline[user]:
            timeline[user][appname] = {}

        if time in timeline[user][appname]:
            timeline[user][appname][time].merge(data)
        else:
            #print time, data.time
            timeline[user][appname][time] = data 

    return timeline

def detect_periodicity(timeline_user_app, user, appname, rounding=1, upper=60):
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
#            print period_index, time_offset, len(total_counter), len(total_counter[period_index]), total_counter[period_index][time_offset]
            total_counter[period_index][time_offset] += 1
            if i in timeline:
#                print i, period_index+2
                range_counter[period_index][time_offset] += 1
                items[period_index][time_offset].append(timeline[i])

    # Evaluate periodic data
    candidate_periods = set()
    for i in range(2,range_steps):
        for j in range(len(range_counter[i-2])):
#            if "facebook" in appname:
#                print i, j, total_counter[i-2][j], range_counter[i-2][j]
            if total_counter[i-2][j] > DATA_POINTS_NEEDED and \
                    range_counter[i-2][j]/float(total_counter[i-2][j]) > CUTOFF:

                valid_period = True
                for n in candidate_periods:
                    if i % n == 0:
                        valid_period = False
                        continue
                if valid_period:
                    candidate_periods.add(i)
                    print user, appname, "period of", i, "data points", total_counter[i-2][j], range_counter[i-2][j]
                
    return range_counter

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
#    timeline = get_data(100000)
    timeline = get_data()
    #timeline = get_data_validate()
    for user, applist in timeline.iteritems():
        for appname, flow in applist.iteritems():
            print "by five minutes..."
            detect_periodicity(flow, user, appname, 5, 60)
            print "by hour..."
            detect_periodicity(flow, user, appname, 60, 3600)

