#!/usr/bin/python

from collections import defaultdict
import operator
import c_session

import parse_wifi
# High-level analysis of top apps


appname_mapping = {"/system/bin/mediaserver":"mediaserver",\
        "com.instagram.android":"instagram",\
        "com.bambuna.podcastaddict":"podcastaddict",\
        "android.process.media":"media_process",\
        "com.facebook.katana":"facebook",\
        "com.android.browser":"google_browser",\
        "au.com.shiftyjelly.pocketcasts":"pocketcasts",\
        "com.google.android.music:main":"google_music",\
        "com.android.chrome":"chrome",\
        "com.dropbox.android":"dropbox",\
        "com.andrewshu.android.reddit":"reddit",\
        "com.google.android.apps.maps":"maps",\
        "com.google.android.gm":"gmail",\
        "com.sec.android.gallery3d":"gallery3d",\
        "com.wssyncmldm":"device_manager",\
        "com.android.vending":"play_store",\
        "com.google.android.apps.plus":"plus",\
        "com.twitter.android":"twitter"}

blacklist = ["com.mobiperf", "com.att.resesarch.mpfstandalone"]

class HostStatistics:

    def __init__(self):
        # [ ] breakdown by encrypted vs not encrypted

        self.encrypted = 0
        self.cleartext = 0

        # [ ] by upload vs not upload
        self.upload = 0
        self.download = 0

        # [ ] by radio energy (total) and average radio breakdown per byte

        self.energy_active = 0
        self.energy_tail = 0

        # [ ] by technology used
        self.byte_wifi = 0
        self.byte_cellular = 0
        self.energy_wifi = 0
        self.energy_cellular = 0

    def add_request(self, size_up, size_down, active_energy, tail_energy, is_encrypted, is_wifi):

        if is_encrypted:
            self.encrypted += (size_up + size_down)
        else:
            self.cleartext += (size_up + size_down)
        
        if is_wifi:
            self.byte_wifi += (size_up + size_down)
            self.energy_wifi += (active_energy + tail_energy)
        else:
            self.byte_cellular += (size_up + size_down)
            self.energy_cellular += (active_energy + tail_energy)

        self.upload += size_up
        self.download += size_down

        self.energy_active += active_energy
        self.energy_tail += tail_energy

    def print_stats(self, f, name):
        print >>f, name, self.encrypted, self.cleartext, self.upload, self.download, self.energy_active, self.energy_tail, self.byte_wifi, self.byte_cellular, self.energy_wifi, self.energy_cellular 

class UserStatistics:
    def __init__(self):

        self.encrypted = 0
        self.cleartext = 0

        # [ ] by data consumed
        self.upload = 0
        self.download = 0
        # [ ] by network energy consumed
        self.energy_active = 0
        self.energy_tail = 0
        # [ ] by requests over WiFi vs not WiFi
        self.byte_wifi = 0
        self.byte_cellular = 0
        # [ ] by time on WiFi vs not wifi TODO
        self.time_wifi = 0
        self.time_cellular = 0

        # [ ] By top 5 apps
        self.app_data_tracker = defaultdict(int)

    def add_request(self, size_up, size_down, active_energy, tail_energy, is_encrypted, is_wifi, appname):

        self.upload += size_up
        self.download += size_down

        self.energy_active += active_energy
        self.energy_tail += tail_energy

        if is_encrypted:
            self.encrypted += (size_up + size_down)
        else:
            self.cleartext += (size_up + size_down)
        
        if is_wifi:
            self.byte_wifi += (size_up + size_down)
        else:
            self.byte_cellular += (size_up + size_down)

        self.app_data_tracker[appname] += (size_up + size_down)

    def add_wifi_data(self, network_type, time):
        if network_type == "wifi":
            self.time_wifi += time
        else:
            self.time_cellular += time

    def print_user_data(self, f):
        print >>f, self.upload, self.download, self.energy_active + self.energy_tail, self.energy_active, self.energy_tail, self.encrypted, self.cleartext, self.byte_wifi, self.byte_cellular, self.time_wifi, self.time_cellular


    def get_top_apps(self, d, num_apps):
        ordered_apps = sorted(self.app_data_tracker.items(), key=operator.itemgetter(1), reverse=True)

        for i in range(min(len(ordered_apps), num_apps)):
                d[ordered_apps[i][0]] += 1
        return d

host_statistics = defaultdict(HostStatistics) 
user_statistics = defaultdict(UserStatistics)

############################ Analyze WiFi trends ###################################

wifi_data = parse_wifi.load_by_user()

for user, user_flow in wifi_data.iteritems():
    for entry in user_flow:
        network_type = entry.other_data["network_type"]
        delta_time = entry.end_time - entry.begin_time

        user_statistics[user].add_wifi_data(network_type, delta_time)
############################  Analyze flows ########################################

flows = c_session.CFlow()

flows.load_data()
#flows.load_data(limit=500000)

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


for item in flows.data:
    userid = item["userID"]
    is_encrypted = (len(item["host"]) == 0)

    app = item["app_name"]

    if app in blacklist:
        continue

    size_up = item["total_dl_payload_h"]
    size_down = item["total_ul_payload_h"]
    time = item["start_time"]
    print item["network_type"]
    is_wifi = (item["network_type"] == 0)
    user= item["userID"]

    energy_active = item["active_energy"]
    energy_tail = item["passive_energy"]

    if app in appname_mapping:
        app = appname_mapping[app]

    if app in test_hosts:
        host_statistics[app].add_request(size_up, size_down, energy_active, energy_tail, is_encrypted, is_wifi)
    user_statistics[user].add_request(size_up, size_down, energy_active, energy_tail, is_encrypted, is_wifi, app)
    

f = open("output_files/app_summary.txt", "w")
for host in test_hosts:
    if host in appname_mapping:
        host = appname_mapping[host]
    host_statistics[host].print_stats(f, host)
f.close()


top_5_apps = defaultdict(int)

f = open("output_files/user_summary.txt", "w")
for k, v in user_statistics.iteritems():
    v.print_user_data(f)
    top_5_apps = v.get_top_apps(top_5_apps, 10)
f.close()

f = open("output_files/top_apps_by_user.txt", "w")

ordered_apps = sorted(top_5_apps.items(), key=operator.itemgetter(1), reverse=True)
for item in ordered_apps:
    print >>f, item[0], item[1]
f.close()

#    if len(urls) != len(hosts) or len(urls) != len(energy_list):
#        if "fonts.googleapis.com" in hosts and len(urls) == 3:
#            urls = [urls[0] + "|" + urls[1], ""]
#        else:
#            if False:
#                continue

