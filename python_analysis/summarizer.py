#!/usr/bin/python

from collections import defaultdict
from scipy.stats.stats import pearsonr

import operator
import c_session

import numpy
import parse_wifi
# High-level analysis of top apps

#host_rank_file = "output_files/top_energy_ratio_hosts_overall.txt"
host_rank_file = "output_files/top_total_hosts.txt"
#host_rank_file = "output_files/top_energy_hosts.txt"
#suffix = "_by_energy_ratio"
suffix = "_by_energy"
#suffix = ""
#suffix = "_by_data_limited"
#suffix = "_by_energy_limited"

appname_mapping = {"/system/bin/mediaserver":"mediaserver",\
        "com.instagram.android":"instagram",\
        "com.bambuna.podcastaddict":"podcastaddict",\
        "android.process.media":"media_process",\
        "com.yhc.magicbus":"campus_bus",\
        "com.yahoo.mobile.client.android.weather":"yahoo_weather",\
        "com.weather.Weather":"weather",\
        "com.facebook.katana:dash":"facebook",\
        "com.google.android.gms":"play_services",\
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
        "com.twitter.android":"twitter",\
        "com.google.process.gapps":"google_apps",\
        "com.google.android.gsf.login":"google_login",\
        "com.renren.xiaonei.android":"renren",\
        "com.google.android.youtube":"youtube",\
        "com.espn.score_center":"espn",\
        "com.accuweather.android":"accuweather",\
        "com.sec.android.widgetapp.ap.hero.accuweather":"accuweather_widget",\
        "com.android.email":"android_email",\
        "com.spotify.mobile.android.service":"spotify"}


appname_mapping = {"com.bambuna.podcastaddict":"podcastaddict",\
        "com.google.android.apps.plus":"plus",\
        "com.instagram.android":"instagram",\
        "au.com.shiftyjelly.pocketcasts":"pocketcasts",\
        "com.google.android.youtube":"youtube",\
        "com.dropbox.android":"dropbox",\
        "com.facebook.katana":"facebook",\
        "com.android.browser":"google_browser",\
        "com.andrewshu.android.reddit":"reddit",\
        "com.android.chrome":"chrome",\
        "com.google.android.music":"google_music",\
        "com.google.android.gm":"gmail",\
        "com.google.android.apps.maps":"maps",\
        "com.twitter.android":"twitter",\
        "com.sina.weibo.servant":"weibo",\
        "com.weather.Weather":"weather",\
        "com.sec.spp.push":"samsung_push",\
        "com.espn.score_center":"espn"}

blacklist = ["com.mobiperf", "com.att.resesarch.mpfstandalone"]

class AppStatistics:

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

        # by code
        self.byte_by_fg = defaultdict(int)
        self.energy_by_fg = defaultdict(int)
        
        self.avg_energy_ratio_cellular = []
        self.avg_energy_ratio_wifi = []

        self.avg_length_session = []
        self.avg_active_length_session = []
        self.avg_ratio_length_session = []
        self.avg_energy_tail_session = []
        self.avg_energy_active_session = []
        self.avg_energy_total_session = []
        self.avg_energy_ratio_session = []
        self.avg_data_session = []

    def add_request(self, size_up, size_down, active_energy, tail_energy, is_encrypted, is_wifi, fg_code, appname, sort_apps):

        if is_encrypted:
            self.encrypted += (size_up + size_down)
        else:
            self.cleartext += (size_up + size_down)
        
        if is_wifi:
            self.byte_wifi += (size_up + size_down)
            self.energy_wifi += (active_energy + tail_energy)

            if size_up + size_down > 0:
                self.avg_energy_ratio_wifi.append((active_energy + tail_energy)/ (size_up + size_down))

        else:
            self.byte_cellular += (size_up + size_down)
            self.energy_cellular += (active_energy + tail_energy)
            if size_up + size_down > 0:
                self.avg_energy_ratio_cellular.append((active_energy + tail_energy)/ (size_up + size_down))

        self.byte_by_fg[fg_code] += (size_up + size_down)
        self.energy_by_fg[fg_code] += (active_energy + tail_energy) 

        self.upload += size_up
        self.download += size_down

        self.energy_active += active_energy
        self.energy_tail += tail_energy


#        if appname != "none":
#            if suffix  == "" or suffix ==  "_by_data_limited" and not is_wifi:
#                sort_apps[appname] += (size_up + size_down)
#            elif suffix == "_by_energy" or suffix == "_by_energy_limited":
#                sort_apps[appname] += (active_energy + tail_energy)
#            else:
#                if size_up + size_down > 0 and not is_wifi:
#                    sort_apps[appname].append((active_energy + tail_energy)/ (size_up + size_down))

    def add_session(self, total_length, active_length, energy_tail, energy_active, data):
        self.avg_length_session.append(total_length)
        self.avg_active_length_session.append(active_length)
        self.avg_ratio_length_session.append(active_length/total_length)
        self.avg_energy_tail_session.append(energy_tail)
        self.avg_energy_active_session.append(energy_active)
        
        self.avg_energy_total_session.append(energy_tail + energy_active)
        if energy_tail + energy_active == 0:
            self.avg_energy_ratio_session.append(0)
        else:
            self.avg_energy_ratio_session.append(energy_tail/(energy_tail + energy_active))

        self.avg_data_session.append(data)

    def print_stats(self, f, name):

        print "=============== ", name, " ================="
        print "length and time active", pearsonr(self.avg_length_session, self.avg_active_length_session)
        print "length and ratio active", pearsonr(self.avg_length_session, self.avg_ratio_length_session)
        print "length and total energy", pearsonr(self.avg_length_session, self.avg_energy_total_session)
        print "length and tail energy ratio", pearsonr(self.avg_length_session, self.avg_energy_ratio_session)
        print "length and data consumed", pearsonr(self.avg_length_session, self.avg_data_session)
        print "length active and time active", pearsonr(self.avg_active_length_session, self.avg_active_length_session)
        print "length active and ratio active", pearsonr(self.avg_active_length_session, self.avg_ratio_length_session)
        print "length active and total energy", pearsonr(self.avg_active_length_session, self.avg_energy_total_session)
        print "length active and tail energy ratio", pearsonr(self.avg_active_length_session, self.avg_energy_ratio_session)
        print "length active and data consumed", pearsonr(self.avg_active_length_session, self.avg_data_session)

        print "energy and data", pearsonr(self.avg_energy_total_session, self.avg_data_session)

        avg_length_session = 0
        if len(self.avg_length_session) > 0:
            avg_length_session = numpy.mean(self.avg_length_session)

        avg_active_length_session = 0
        if len(self.avg_active_length_session) > 0:
            avg_active_length_session = numpy.mean(self.avg_active_length_session)

        avg_energy_tail_session = 0
        if len(self.avg_energy_tail_session) > 0:
            avg_energy_tail_session = numpy.mean(self.avg_energy_tail_session)

        avg_energy_active_session = 0
        if len(self.avg_energy_active_session) > 0:
            avg_energy_active_session = numpy.mean(self.avg_energy_active_session)

        avg_data_session = 0
        if len(self.avg_data_session) > 0:
            avg_data_session = numpy.mean(self.avg_data_session)

        avg_ratio_wifi = 0
        if len(self.avg_energy_ratio_wifi) > 0:
            avg_ratio_wifi = numpy.mean(self.avg_energy_ratio_wifi) 

        avg_ratio_cellular = 0
        if len(self.avg_energy_ratio_cellular) > 0:
            avg_ratio_cellular = numpy.mean(self.avg_energy_ratio_cellular) 

        print >>f, name, self.encrypted, self.cleartext, self.upload, \
                self.download, self.energy_active, self.energy_tail, \
                self.byte_wifi, self.byte_cellular, self.energy_wifi, \
                self.energy_cellular, avg_length_session, \
                avg_active_length_session, avg_energy_tail_session, \
                avg_energy_active_session, avg_data_session, avg_ratio_wifi,\
                avg_ratio_cellular, \
                self.byte_by_fg[400], self.energy_by_fg[400],\
                self.byte_by_fg[100], self.energy_by_fg[100],\
                self.byte_by_fg[130], self.energy_by_fg[130],\
                self.byte_by_fg[300], self.energy_by_fg[300],\
                self.byte_by_fg[200], self.energy_by_fg[200]

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

        self.energy_wifi = 0
        self.energy_cellular = 0

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
            self.energy_wifi += (active_energy + tail_energy)
        else:
            self.byte_cellular += (size_up + size_down)
            self.energy_cellular += (active_energy + tail_energy)
        if appname != "none":
            self.app_data_tracker[appname] += (size_up + size_down)

    def add_wifi_data(self, network_type, time):
        if time < 0:
            return
        if network_type == "wifi":
            self.time_wifi += time
        else:
            self.time_cellular += time

    def print_user_data(self, f):
        print >>f, self.upload, self.download, self.energy_active + self.energy_tail, self.energy_active, self.energy_tail, self.energy_wifi, self.energy_cellular, self.encrypted, self.cleartext, self.byte_wifi, self.byte_cellular, self.time_wifi, self.time_cellular


    def get_top_apps(self, d, num_apps):
        ordered_apps = sorted(self.app_data_tracker.items(), key=operator.itemgetter(1), reverse=True)
        for i in range(min(len(ordered_apps), num_apps)):
                
                d[ordered_apps[i][0]] += 1
        return d

app_statistics = defaultdict(AppStatistics) 
app_statistics_wifi = defaultdict(AppStatistics)

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

#flows.load_data(min_time = 1377129600, max_time=1380758400)
flows.load_data()
#flows.load_data(limit=500000)

if suffix == "_by_energy_ratio":
    sort_apps = defaultdict(list)
else:
    sort_apps = defaultdict(int)

#test_hosts = []
#f = open(host_rank_file)
#limit = 25 
#for line in f:
#    line = line.split()[0]
#    if line in appname_mapping:
#        line = appname_mapping[line]
#
#    test_hosts.append(line)
#    limit -= 1
#    if limit == 0:
#        break
#f.close()

# Get data per flow
for item in flows.data:
    userid = item["userID"]
    is_encrypted = (len(item["host"]) == 0)

    app = item["app_name"].split(":")[0]

    if app in blacklist:
        continue

    size_up = item["total_dl_whole"]
    size_down = item["total_ul_whole"]
    time = item["start_time"]
#    if time < 1377129600:
#        continue
#    if time > 1380758400:
#        continue

#    print item["network_type"]
    is_wifi = (item["network_type"] == 0)
    user= item["userID"]

    energy_active = item["active_energy"]
    energy_tail = item["passive_energy"]

    fg_log = item["fg_log"]
    fg_code = -1
    if len(fg_log) > 0:
        fg_log.sort(key=operator.itemgetter(1))
        fg_code = fg_log[0][0]

    if app in appname_mapping:
        app = appname_mapping[app]

#    if app in test_hosts:
    if is_wifi:
        app_statistics_wifi[app].add_request(size_up, size_down, \
                energy_active, energy_tail, is_encrypted, is_wifi, fg_code, app, sort_apps)
#        print "here"
    else:
        app_statistics[app].add_request(size_up, size_down, \
                energy_active, energy_tail, is_encrypted, is_wifi, fg_code, app, sort_apps)

    user_statistics[user].add_request(size_up, size_down, \
            energy_active, energy_tail, is_encrypted, is_wifi, app)
    
############################  Analyze sessions ########################################
f = open("output_files/session_summary.txt")
unique_appnames = set()
for line in f.readlines():
    line = line.split()

    active_apps = int(line[10])
    if active_apps == 0:
        continue

    session_id = line[0]
    total_length = float(line[1])
    active_length = float(line[2])
    energy_tail = float(line[3])
    energy_active = float(line[4])
    had_wifi = line[5] == "0"
    data = int(line[7]) + int(line[8])
    active_app_list = []
    if len(line) > 12:
        active_app_list = line[13:]

        print line
        print active_app_list
        print total_length
    unique_appnames.update(active_app_list)
    if total_length == 0:
        continue

    for app in active_app_list:
        if app in appname_mapping:
            app = appname_mapping[app]
#        if app in test_hosts:
        if had_wifi:
            app_statistics_wifi[app].add_session(total_length, active_length, energy_tail, energy_active, data)
        else:
            app_statistics[app].add_session(total_length, active_length, energy_tail, energy_active, data)
  
f.close()

if suffix == "_by_energy_ratio":
    for k in sort_apps.keys():
        sort_apps[k] = numpy.mean(sort_apps[k])


if suffix == ""or suffix ==  "_by_data_limited":

    for host, data in app_statistics.iteritems():
        sort_apps[host] = data.upload + data.upload

if suffix == "_by_energy" or suffix ==  "_by_energy_limited":

    for host, data in app_statistics.iteritems():
        sort_apps[host] = data.energy_tail + data.energy_active

test_hosts = sorted(sort_apps.items(), key = operator.itemgetter(1), reverse=True)

#            if suffix  == "" or suffix ==  "_by_data_limited" and not is_wifi:
#                sort_apps[appname] += (size_up + size_down)
#            elif suffix == "_by_energy" or suffix == "_by_energy_limited":
#                sort_apps[appname] += (active_energy + tail_energy)
#            else:
#                if size_up + size_down > 0 and not is_wifi:
#                    sort_apps[appname].append((active_energy + tail_energy)/ (size_up + size_down))

f = open("output_files/app_summary_ratio.txt", "w")
ratio_hosts = ["com.android.browser", "com.android.chrome", "com.espn.score_center", "com.facebook.katana", "com.instagram.android", "com.google.android.apps.plus", "com.twitter.android", "com.weather.Weather", "com.sina.weibo.servant", "com.google.android.apps.maps", "au.com.shiftyjelly.pocketcasts", "com.bambuna.podcastaddict", "com.spotify.mobile.android.service", "com.google.android.gm", "com.sec.spp.push", "com.skype.raider"]

for host in ratio_hosts:
    if host in appname_mapping:
        host = appname_mapping[host]
    app_statistics[host].print_stats(f, host)
f.close()

limit = 25
f = open("output_files/app_summary" + suffix + ".txt", "w")
#for host in appname_mapping.values():
for host in test_hosts:

    host = host[0]
    if limit == 0:
        break
    limit -= 1

    if host in appname_mapping:
        host = appname_mapping[host]
    app_statistics[host].print_stats(f, host)
f.close()

limit = 25
f = open("output_files/app_summary_wifi"+ suffix +".txt", "w")
for host in test_hosts:
    host = host[0]
    if limit == 0:
        break
    limit -= 1

    if host in appname_mapping:
        host = appname_mapping[host]
    app_statistics_wifi[host].print_stats(f, host)
f.close()

top_5_apps = defaultdict(int)

f = open("output_files/user_summary" + suffix + ".txt", "w")
for k, v in user_statistics.iteritems():
    v.print_user_data(f)
    top_5_apps = v.get_top_apps(top_5_apps, 10)
f.close()

f = open("output_files/top_apps_by_user" + suffix + ".txt", "w")

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

