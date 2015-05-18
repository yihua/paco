#!/usr/bin/python

# TODO: break up session by active app

import numpy
import timestream
from collections import defaultdict
import operator
import glob

app_session_data = {"/system/bin/mediaserver":"mediaserver.txt",\
        "com.instagram.android":"instagram.txt",\
        "com.bambuna.podcastaddict":"podcastaddict.txt",\
        "android.process.media":"media.txt",\
        "com.facebook.katana":"facebook.txt",\
        "com.android.browser":"browser.txt",\
        "au.com.shiftyjelly.pocketcasts":"shiftyjelly.txt",\
        "com.google.android.music:main":"music.txt",\
        "com.android.chrome":"chrome.txt",\
        "com.dropbox.android":"dropbox.txt",\
        "none":"none.txt",\
        "com.andrewshu.android.reddit":"reddit.txt",\
        "com.google.android.apps.maps":"maps.txt",\
        "com.google.android.gm":"gmail.txt",\
        "com.sec.android.gallery3d":"gallery3d.txt",\
        "com.wssyncmldm":"device_manager.txt",\
        "com.android.vending":"vending.txt",\
        "com.google.android.apps.plus":"plus.txt",\
        "com.twitter.android":"twitter.txt",\
        "com.clearchannel.iheartradio.controller":"iheartradio.txt"} 

class ForegroundAttribute(timestream.AttributeItem):
    def __init__(self, user, timestamp):
        other_data = {"foreground_apps":[], }
        timestream.AttributeItem.__init__(self, user, timestamp, timestamp, other_data)

    def setTime(self, time):
        self.end_time = time

    def add_app(self, appname):
        self.other_data["foreground_apps"].append(appname)

class SessionAttribute(timestream.AttributeItem):
    
    def __init__(self, user, begin_time, end_time, active_time, session_id, num_clicks, is_session):

        self.energy_tail_fg = 0
        self.energy_active_fg = 0
        self.energy_tail_bg = 0
        self.energy_active_bg = 0

        self.byte_upload_fg = 0
        self.byte_download_fg = 0
        self.byte_upload_bg = 0
        self.byte_download_bg = 0

        self.byte_encrypted_fg = 0
        self.byte_encrypted_bg = 0

        self.num_requests_fg = 0
        self.num_requests_bg = 0

        # Not mutually exclusive
        self.had_wifi = False
        self.had_cellular = False

        self.active_apps = set()
        self.passive_apps = set()

        self.active_apps_time = defaultdict(list)

        self.is_session = is_session
        self.num_clicks = num_clicks

        self.host_data = {}

        other_data = {"session_id": session_id, "session_length": end_time - begin_time, "active_session_length": active_time}
        timestream.AttributeItem.__init__(self, user, begin_time, end_time, other_data)
    
    def merge_foreground_item(self, foreground_item):
        for appname in foreground_item.other_data["foreground_apps"]:
            self.active_apps_time[appname].append([float(foreground_item.begin_time), float(foreground_item.end_time)])

    def merge_timeline_item(self, timeline_item):
        if isinstance(timeline_item, ForegroundAttribute):
            self.merge_foreground_item(timeline_item)
            return

        times_raw = timeline_item.data["timestamp_log"]

        upload_data =  timeline_item.data["total_ul_whole"]
        download_data =  timeline_item.data["total_dl_whole"]
        appname = timeline_item.data["app_name"].split(":")[0]

        fg_log = timeline_item.data["fg_log"]
        if len(fg_log) > 0:
            fg_log.sort(key=operator.itemgetter(1))
        fg_code = []
        for item in fg_log:
            if item[1]*1000 > self.begin_time and item[1]*1000 < self.end_time and item[0] != -1:
                fg_code.append(item[0])

        if appname not in self.host_data:
            self.host_data[appname] = {}
        print times_raw
        for i, time in enumerate(times_raw):
            if len(time) == 0:
                continue
            try:
                begin_time, end_time = time.split(",")
                begin_time = float(begin_time)
                end_time = float(end_time)
                if begin_time > 2000000000:
                    begin_time = begin_time/1000
                else:
                    time = int(float(begin_time)*1000)
                if end_time > 2000000000:
                    end_time = begin_time/1000

                if end_time < begin_time:
                    temp = end_time
                    end_time = max(end_time, begin_time)
                    begin_time = min(begin_time, temp)
                     
            except:
                print "error, continuing!"
                continue
                
            fg_code_local = -1
            for item in fg_log:
                if item[1] <= begin_time and item[2] <= end_time:
                    fg_code_local = item[0]
                    break

            if fg_code_local == 100 or fg_code_local == 300 :
                self.num_requests_fg += 1
#                self.active_apps_time[appname].append([begin_time, end_time])
            elif fg_code_local != -1:
                self.num_requests_bg += 1

            if i < len(timeline_item.data["request_url"]) and \
                    i < len(timeline_item.data["content_type"]) and \
                    i < len(timeline_item.data["energy_log"]) and \
                    i < len(timeline_item.data["content_length"]):

                if time not in self.host_data[appname]:
                    self.host_data[appname][time] = []

                (energy_active, energy_passive) = timeline_item.data["energy_log"][i].split(",")
                energy_active = float(energy_active)
                energy_passive = float(energy_passive)

                self.host_data[appname][time].append([timeline_item.data["request_url"][i],\
                        timeline_item.data["content_type"][i],\
                        timeline_item.data["content_length"][i], 0, \
                        energy_active, energy_passive, fg_code_local])

        tail_energy = timeline_item.data["passive_energy"]
        active_energy = timeline_item.data["active_energy"]

        if 100 in fg_code or 200 in fg_code:
            self.energy_tail_fg += tail_energy 
            self.energy_active_fg += active_energy 
            self.byte_upload_fg += upload_data 
            self.byte_download_fg += download_data 
        elif 400 in fg_code or 130 in fg_code or 300 in fg_code:
            self.energy_tail_bg += tail_energy 
            self.energy_active_bg += active_energy 
            self.byte_upload_bg += upload_data 
            self.byte_download_bg += download_data 

        if timeline_item.data["is_wifi"]:
            self.had_wifi = True
        else:
            self.had_cellular = True

        if timeline_item.data["flow_encrypted"]:
            if 100 in fg_code or 200 in fg_code:  
                self.byte_encrypted_fg += upload_data + download_data
            elif 400 in fg_code or 130 in fg_code or 300 in fg_code:
                self.byte_encrypted_bg += upload_data + download_data

        if 100 in fg_code or 200 in fg_code: 
            self.active_apps.add(appname)
        elif 400 in fg_code or 130 in fg_code or 300 in fg_code:
            self.passive_apps.add(appname)

    def find_time_active(self, begin_time, end_time, active_apps_time):
        if begin_time > 20000000000:
            begin_time = begin_time/1000.0
        if end_time > 20000000000:
            end_time = end_time/1000.0

        for item in active_apps_time:
            if item[0] > 20000000000:
                item[0] = item[0]/1000.0
            if item[1] > 20000000000:
                item[1] = item[1]/1000.0

        working_list = active_apps_time[:]
        for item in active_apps_time:
            new_list = []

            if item in working_list:
                working_list.remove(item)
            else:
                continue
            
            for item2 in working_list:
                if (item2[1] < item[0] or item2[0] > item[1]):
                    new_list.append(item2)
                else:
                    item[0] = min(item[0], item2[0])
                    item[1] = max(item[1], item2[1])


            item[0] = max(begin_time, item[0])
            item[1] = min(end_time, item[1])
            new_list.append(item)
            working_list = new_list[:]

        total_time = end_time - begin_time
        active_time = 0.0
        for item in working_list:
            active_time += item[1] - item[0]
        if total_time == 0:
            print begin_time, end_time
            return -1
        return float(active_time)/total_time

    def print_apps(self, app_files, app_summary_d):
        for app, app_timeline in self.host_data.iteritems():
            if app in app_files:

#                print self.active_apps_time
                percent_active = self.find_time_active(self.begin_time, self.end_time, self.active_apps_time[app])
                #percent_active = 0
                print >>app_files[app], self.had_wifi, self.energy_active_fg, \
                        self.energy_tail_fg, self.byte_upload_fg, \
                        self.byte_download_fg, len(self.active_apps), \
                        self.num_requests_fg, self.energy_active_bg, \
                        self.energy_tail_bg, self.byte_upload_bg, \
                        self.byte_download_bg, len(self.passive_apps), \
                        self.num_requests_bg, percent_active

                app_data = 0
                app_energy = 0
                
                time = app_timeline.keys()
                time.sort()
                first_time = 0
                for t in time:
                    if first_time == 0:
                        first_time = t
                    delta_t = t - first_time

                    # url, content type, avg_data_up, avg_data_down, energy_active, energy_passive, fg_code
                    for item in app_timeline[t]:
                        if len(item) >= 7:
                            fg_code = item[6]
                            if fg_code == 100 or fg_code == 300:
                                try:
                                    app_data += int(item[2]) + item[3]
                                except:
                                    pass
                                try:
                                    app_energy += float(item[4]) + float(item[5])
                                except:
                                    pass
                            print >> app_files[app], self.other_data["session_id"], delta_t, item[0], item[1], \
                                    item[2], item[3], item[4], item[5], item[6]
                print >>app_files[app]
                
#                print app_summary_d, percent_active
                if app_summary_d != None and percent_active > 0:
                    app_summary_d[app]["active"].append(percent_active)
                    app_summary_d[app]["length"].append(self.end_time - self.begin_time)
                    app_summary_d[app]["length_active"].append((self.end_time - self.begin_time)* percent_active)
                    if app_data > 0:
                        app_summary_d[app]["data_app"].append(app_data)
                    app_summary_d[app]["data_total"].append(self.byte_upload_fg + self.byte_download_fg)
                    if app_energy > 0:
                        app_summary_d[app]["energy_app"].append(app_energy)
                    app_summary_d[app]["energy_total"].append(self.energy_tail_fg + self.energy_active_fg)
                    app_summary_d[app]["other_apps"].append(len(self.active_apps))
                    app_summary_d[app]["other_apps_background"].append(len(self.passive_apps))

    def print_summary(self, f, user_summaries):
        if self.had_wifi:
            self.had_wifi = 1
        else:
            self.had_wifi = 0

        if self.had_cellular:
            self.had_cellular = 1
        else:
            self.had_cellular = 0

        percent_active = []
        for app in self.active_apps:
            p = self.find_time_active(self.begin_time, self.end_time, self.active_apps_time[app])
#            p = 0
            if p > 0:
                percent_active.append(p)

        if user_summaries != None:
            user_summaries["length"][user].append(self.end_time - self.begin_time)
            user_summaries["energy"][user].append(self.energy_tail_fg + self.energy_active_fg)
            user_summaries["data"][user].append(self.byte_upload_fg+self.byte_download_fg)
            user_summaries["other_count"][user].append(len(self.active_apps))
            user_summaries["background_count"][user].append(len(self.passive_apps))

            if user not in user_summaries["total_length"]:
                user_summaries["total_length"][user] = 0
            user_summaries["total_length"][user] += self.end_time - self.begin_time

        print >>f, self.other_data["session_id"], \
                self.other_data["session_length"], \
                self.other_data["active_session_length"], \
                self.energy_tail_fg, self.energy_active_fg, \
                self.had_wifi, self.had_cellular,\
                self.byte_upload_fg, self.byte_download_fg,\
                self.byte_encrypted_fg,\
                len(self.active_apps),\
                self.begin_time,\
                self.end_time,\
                "-".join(self.active_apps), \
                self.energy_tail_bg, self.energy_active_bg, \
                self.byte_upload_bg, self.byte_download_bg,\
                self.byte_encrypted_bg,\
                len(self.passive_apps),\
                "-".join(self.passive_apps)

def load_foreground_data(limit=-1):
    timestream = defaultdict(list)
    dirs = glob.glob("/nfs/beirut2/ashnik/active_data/active_sorted_*")
    
    cur_item = None

    user_last_time = defaultdict(int)
    user_last_entry = {}

    for name in dirs:
        f = open(name)
        for line in f.readlines():
            
            if limit != -1:
                if limit == 0:
                    return timestream
                else:
                    limit -= 1

            (imei, time, appname, is_foreground) = line.split()

            if appname not in app_session_data:
                continue

            if imei not in user_last_time:
                user_last_time[imei] = time
                continue

            if user_last_time[imei] != time and imei in user_last_entry and \
                    user_last_entry[imei] != None and \
                    len(user_last_entry[imei].other_data["foreground_apps"]) > 0:
                user_last_entry[imei].setTime(time)
                timestream[imei].append(user_last_entry[imei])
                user_last_entry[imei] = ForegroundAttribute(imei, time)
            
            user_last_time[imei] = time            

            if not is_foreground == "100" or is_foreground == "300":
                continue

            if imei not in user_last_entry:
                user_last_entry[imei] = ForegroundAttribute(imei, time)

            user_last_entry[imei].add_app(appname)

    return timestream

#    f = open("/nfs/beirut1/userstudy/2nd_round/active_fg")
#    last_time = {}
#    last_attribute = {}
#    for line in f.readlines():
#        (imei, time, appname) = line.split()
#
#        time = float(time)*1000
#
#        if imei in last_time and time != last_time[imei]:
#            if imei in last_attribute:
#                timestream[imei].append(last_attribute[imei])
#            last_attribute[imei] = ForegroundAttribute(imei, time, appname)
#        else:
#            if imei not in last_attribute:
#                last_attribute[imei] = ForegroundAttribute(imei, time, appname)
#            else:
#                last_attribute[imei].add_app(appname)
#
#        last_time[imei] = time 
#    return timestream

def load_session_data(limit=-1):
    timestream = defaultdict(list)
    f = open("/z/user-study-imc15/PACO/user_session_summary.txt")
    for line in f.readlines():
        if limit != -1:
            if limit == 0:
                return timestream
            else:
                limit -= 1
        (userid, start_time, end_time, active_time, session_id, discard_1, discard_2, num_clicks, is_session) = line.split()
        end_time = float(end_time)*1000
        start_time = float(start_time)*1000
        active_time = float(active_time)
        num_clicks = int(num_clicks)
        if is_session != "1" or start_time > end_time:
            continue

        timestream[userid].append(SessionAttribute(userid, start_time, end_time, active_time, session_id, num_clicks, is_session))
    return timestream

def print_app_cdf(f, app_summary_d):
    active = app_summary_d["active"]
    active.sort()
    length = app_summary_d["length"]
    length.sort()
    length_active = app_summary_d["length_active"]
    length_active.sort()
    data_app = app_summary_d["data_app"]
    data_app.sort()
    data_total = app_summary_d["data_total"]
    data_total.sort()
    energy_app = app_summary_d["energy_app"]
    energy_app.sort()
    energy_total = app_summary_d["energy_total"]
    energy_total.sort()
    other_apps = app_summary_d["other_apps"]
    other_apps.sort()
    other_apps_background = app_summary_d["other_apps_background"]
    other_apps_background.sort()

    l = len(active)
    for i in range(l):
        print >>f, float(i)/l, active[i], length[i], length_active[i], data_app[i], \
                data_total[i], energy_app[i], energy_total[i], other_apps[i],\
                other_apps_background[i]

def print_user_cdf(user_summaries):

    f = open("session_examples/user_summary.txt", "w")
    columns = defaultdict(list)
    active_time = []
    keys = ["length", "energy", "data", "other_count", "background_count"]
    for k in keys:
        for user, data in user_summaries[k].iteritems():
            columns[k].append(numpy.mean(data))

        columns[k].sort()
        print k, columns[k]

    for user, data in user_summaries["total_length"].iteritems():
        active_time.append(data)
    active_time.sort()

    l = len(columns[k])
    for i in range(l):
        print>>f, i/float(l), columns["length"][i], columns["energy"][i], \
                columns["data"][i], columns["other_count"][i], columns["background_count"][i], \
                active_time[i]

    f.close()

if __name__ == "__main__":

    user_summaries = defaultdict(lambda: defaultdict(list)) 
    app_summaries = defaultdict(lambda: defaultdict(list)) 
    

    print "Loading session data..."
    session_timeline = load_session_data()
    print "Session data loaded."
    print "Loading foreground data..."
    foreground_timeline = load_foreground_data()
    print "Foreground data loaded."
    print "Loading timestream data..."
    flow_timeline = timestream.load_timeline()
    print "Timestream data loaded."

#    print foreground_timeline.keys()
#    print session_timeline.keys()

    if False:
        print "Merging foreground data..."
        for user, user_timeline in foreground_timeline.iteritems():
            print user
            if user in session_timeline:
                print "\tMerging foreground data for", user

    #            print "merging!", len(foreground_timeline[user])
    #            print foreground_timeline[user][0].to_string()
    #            print user_timeline[0].time
    #            exit()

                timestream.merge(user_timeline, session_timeline[user], reverse=True)

    print "Merging session data..."
    for user, user_timeline in flow_timeline.iteritems():
        if user in session_timeline:
            print "\tMerging session data for", user
            timestream.merge(user_timeline, session_timeline[user], reverse=True)
    
    app_session_files = {}
    app_nosession_files = {}
    for app, string in app_session_data.iteritems():
        app_session_files[app] = open("session_examples/" + string, "w")
        app_nosession_files[app] = open("session_examples/nosession_" + string, "w")

    f = open("output_files/session_summary.txt", "w")
    g = open("output_files/nosession_summary.txt", "w")

    print "Printing data and aggregating results..."
    for user, session_timeline in session_timeline.iteritems():
        for item in session_timeline:
            if item.is_session:
                item.print_summary(f, user_summaries)
                item.print_apps(app_session_files, app_summaries)
            else:
                item.print_summary(g, None)
                item.print_apps(app_nosession_files, None )
    f.close()
    g.close()

    for f in app_session_files.values():
       f.close()
    for f in app_nosession_files.values():
       f.close()

    print "Printing summary data..."
    print app_summaries.keys()
    g = open("session_examples/app_summary.txt", "w")
    for app, string in app_session_data.iteritems():
        f = open("session_examples/summary_cdf_" + string, "w")
#        print_app_cdf(f, app_summaries[app]) 
        print >>g, app, numpy.mean(app_summaries[app]["active"]), \
                numpy.mean(app_summaries[app]["length"]), \
                numpy.mean(app_summaries[app]["length_active"]), \
                numpy.mean(app_summaries[app]["data_app"]), \
                numpy.mean(app_summaries[app]["data_total"]), \
                numpy.mean(app_summaries[app]["energy_app"]), \
                numpy.mean(app_summaries[app]["energy_total"]), \
                numpy.mean(app_summaries[app]["other_apps"]), \
                numpy.mean(app_summaries[app]["other_apps_background"])
        f.close()
    g.close()
    print_user_cdf(user_summaries)

