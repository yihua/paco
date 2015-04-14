#!/usr/bin/python

# TODO: break up session by active app

import timestream
from collections import defaultdict

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
    def __init__(self, user, timestamp, appname):
        other_data = {"foreground_apps":[appname]}
        timestream.AttributeItem.__init__(self, user, timestamp, timestamp+10, other_data)

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

        self.is_session = is_session
        self.num_clicks = num_clicks

        self.host_data = {}

        other_data = {"session_id": session_id, "session_length": end_time - begin_time, "active_session_length": active_time}
        timestream.AttributeItem.__init__(self, user, begin_time, end_time, other_data)

    def merge_timeline_item(self, timeline_item):
            

        times_raw = timeline_item.data["timestamp_log"]

        upload_data =  timeline_item.data["flow_ul_payload"]
        download_data =  timeline_item.data["flow_dl_payload"]
        appname = timeline_item.data["app_name"].split(":")[0]

        if "foreground_apps" not in timeline_item.data:
            is_foreground = False
        else:
            is_foreground = (timeline_item.data["app_name"] in timeline_item.data["foreground_apps"])

        if appname not in self.host_data:
            self.host_data[appname] = {}

        #print times_raw
        for i, time in enumerate(times_raw):
            try:
                time = int(float(time.split(",")[0])*1000)
            except:
                continue
            #print len(timeline_item.data["request_url"]), len(timeline_item.data["content_type"]), len(timeline_item.data["energy_log"])

            if is_foreground:
                self.num_requests_fg += 1
            else:
                self.num_requests_bg += 1
            if i < len(timeline_item.data["request_url"]) and \
                    i < len(timeline_item.data["content_type"]) and \
                    i < len(timeline_item.data["energy_log"]):

                if time not in self.host_data[appname]:
                    self.host_data[appname][time] = []

                (energy_active, energy_passive) = timeline_item.data["energy_log"][i].split(",")
                energy_active = float(energy_active)
                energy_passive = float(energy_passive)

                self.host_data[appname][time].append([timeline_item.data["request_url"][i],\
                        timeline_item.data["content_type"][i],\
                        upload_data/len(times_raw), download_data/len(times_raw),\
                        energy_active, energy_passive, is_foreground])

        tail_energy = timeline_item.data["passive_energy"]
        active_energy = timeline_item.data["active_energy"]

        if is_foreground:
            self.energy_tail_fg += tail_energy 
            self.energy_active_fg += active_energy 
            self.byte_upload_fg += upload_data 
            self.byte_download_fg += download_data 
        else:
            self.energy_tail_bg += tail_energy 
            self.energy_active_bg += active_energy 
            self.byte_upload_bg += upload_data 
            self.byte_download_bg += download_data 

        if timeline_item.data["is_wifi"]:
            self.had_wifi = True
        else:
            self.had_cellular = True


        if timeline_item.data["flow_encrypted"]:
            if is_foreground:
                self.byte_encrypted_fg += upload_data + download_data
            else:
                self.byte_encrypted_bg += upload_data + download_data

        if is_foreground:
            self.active_apps.add(appname)
        else:
            self.passive_apps.add(appname)

    def print_apps(self, app_files):
        for app, app_timeline in self.host_data.iteritems():
            if app in app_files:
                print >>app_files[app], self.had_wifi, self.energy_active_fg, self.energy_tail_fg, self.byte_upload_fg, self.byte_download_fg, len(self.active_apps), self.num_requests_fg, \
                self.energy_active_bg, self.energy_tail_bg, self.byte_upload_bg, self.byte_download_bg, len(self.passive_apps), self.num_requests_bg
                time = app_timeline.keys()
                time.sort()
                first_time = 0
                for t in time:
                    if first_time == 0:
                        first_time = t
                    delta_t = t - first_time

                    for item in app_timeline[t]:
                        if len(item) >= 7:
                            print >> app_files[app], self.other_data["session_id"], delta_t, item[0], item[1], \
                                    item[2], item[3], item[4], item[5], item[6]
                print >>app_files[app]

    def print_summary(self, f):
        if self.had_wifi:
            self.had_wifi = 1
        else:
            self.had_wifi = 0

        if self.had_cellular:
            self.had_cellular = 1
        else:
            self.had_cellular = 0

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
    f = open("/nfs/beirut1/userstudy/2nd_round/active_fg")
    last_time = {}
    last_attribute = {}
    for line in f.readlines():
        (imei, time, appname) = line.split()

        time = float(time)*1000

        if imei in last_time and time != last_time[imei]:
            if imei in last_attribute:
                timestream[imei].append(last_attribute[imei])
            last_attribute[imei] = ForegroundAttribute(imei, time, appname)
        else:
            if imei not in last_attribute:
                last_attribute[imei] = ForegroundAttribute(imei, time, appname)
            else:
                last_attribute[imei].add_app(appname)

        last_time[imei] = time 
    return timestream

def load_session_data(limit=-1):
    timestream = defaultdict(list)
    f = open("/z/user-study-imc15/PACO/user_session_summary.txt")
    for line in f.readlines():
        (userid, start_time, end_time, active_time, session_id, discard_1, discard_2, num_clicks, is_session) = line.split()
        end_time = float(end_time)*1000
        start_time = float(start_time)*1000
        active_time = float(active_time)
        num_clicks = int(num_clicks)

        timestream[userid].append(SessionAttribute(userid, start_time, end_time, active_time, session_id, num_clicks, is_session))
    return timestream

if __name__ == "__main__":
    session_timeline = load_session_data()
    foreground_timeline = load_foreground_data()
    flow_timeline = timestream.load_timeline()

    for user, user_timeline in flow_timeline.iteritems():
        if user in foreground_timeline:

            print "merging!", len(foreground_timeline[user])
            print foreground_timeline[user][0].to_string()
            print user_timeline[0].time
            exit()

            timestream.merge(user_timeline, foreground_timeline[user])

    for user, user_timeline in flow_timeline.iteritems():
        if user in session_timeline:
            timestream.merge(user_timeline, session_timeline[user], reverse=True)
    
    app_session_files = {}
    app_nosession_files = {}
    for app, string in app_session_data.iteritems():
        app_session_files[app] = open("session_examples/" + string, "w")
        app_nosession_files[app] = open("session_examples/nosession_" + string, "w")

    f = open("output_files/session_summary.txt", "w")
    g = open("output_files/nosession_summary.txt", "w")

    for user, session_timeline in session_timeline.iteritems():
        for item in session_timeline:
            if item.is_session:
                item.print_summary(f)
                item.print_apps(app_session_files)
            else:
                item.print_summary(g)
                item.print_apps(app_nosession_files)
    f.close()
    g.close()

    for f in app_session_files.values():
       f.close()
    for f in app_nosession_files.values():
       f.close()
