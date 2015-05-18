#!/usr/bin/python

from collections import defaultdict
from scipy.stats.stats import pearsonr

import operator
import c_session

import glob
import numpy
import parse_wifi

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

dirs = ["/nfs/beirut2/ashnik/active_data/active_sorted_201210", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201212", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201301", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201302", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201303", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201304", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201305", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201306", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201307", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201308", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201309", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201310", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201311", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201312", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201401", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201402", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201403", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201404", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201405", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201406", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201407", \
        "/nfs/beirut2/ashnik/active_data/active_sorted_201408"]

timeline = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
timeline_visible = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))

#dirs = glob.glob("/nfs/beirut2/ashnik/active_data/active_sorted_*")

cur_item = None
user_last_time_app = defaultdict(dict)
visible_user_last_time_app = defaultdict(dict)

user_last_time = defaultdict(int)
user_last_time_foreground = defaultdict(lambda:False)
visible_user_last_time_foreground = defaultdict(lambda:False)

limit = -1
for name in dirs:
    f = open(name)
    print name
    for line in f:
        if limit != -1:
            if limit > 0:
                limit -= 1
            else:
                break

        (imei, time, appname, is_foreground) = line.split()

        time = int(time)

        if imei not in user_last_time or time - user_last_time[imei] > 60000:
            user_last_time[imei] = time
            user_last_time_foreground[imei] = False
            visible_user_last_time_foreground[imei] = False
            user_last_time_app[imei] = {}
            visible_user_last_time_app[imei] = {}
            continue

        if time != user_last_time[imei]:
            week = int(float(time)/(3600*24*1000))
            # New timeslot: save all old data
            delta_t = (float(time) - float(user_last_time[imei]))
            if delta_t < 0:
                print imei, time, user_last_time[imei]
            else:

                for app in user_last_time_app[imei]:
                    if user_last_time_app[imei][app] == user_last_time[imei]:
                        timeline[week][imei][app] += (float(time) - float(user_last_time[imei])) 
                    
                    if visible_user_last_time_app[imei][app] == user_last_time[imei]:
                        timeline_visible[week][imei][app] += (float(time) - float(user_last_time[imei])) 

                if user_last_time_foreground[imei]: # these are booleans, no compare needed
                    timeline[week][imei]["all"] += float(time) - float(user_last_time[imei])
                
                if visible_user_last_time_foreground[imei]:
                    timeline_visible[week][imei]["all"] += float(time) - float(user_last_time[imei])

            user_last_time_app[imei] = {}
            visible_user_last_time_app[imei] = {}
            user_last_time_foreground[imei] = False
            visible_user_last_time_foreground[imei] = False
            
            user_last_time[imei] = time

#        print time, time-user_last_time[imei]
        if appname not in appname_mapping:
            user_last_time[imei] = time
            continue

#        if appname in user_last_time[imei]:
#            print user_last_time[imei][appname][1]

        if is_foreground == "100" or is_foreground == "200":
            user_last_time_foreground[imei] = True
            user_last_time_app[imei][appname] = time

        if is_foreground == "100" or is_foreground == "300" or is_foreground == "130" or is_foreground == "200":
            visible_user_last_time_foreground[imei] = True
            visible_user_last_time_app[imei][appname] = time

        user_last_time[imei] = time

    f.close()
times = timeline.keys()
times.sort()

print user_last_time.keys()

f = open("app_trends/time_in_foreground_by_user.txt", "w")
for t in times:
    for imei in timeline[t].keys():
        print >>f, t,
        print >>f, imei,
        print >>f, timeline[t][imei]["all"],

        appnames = appname_mapping.keys()
        appnames.sort()
        for app in appnames:
            if app in timeline[t][imei]:
                print >>f, timeline[t][imei][app],
            else:
                print >>f, 0,

        print >>f
    
f = open("app_trends/visible_time_in_foreground_by_user.txt", "w")
for t in times:
    for imei in timeline_visible[t].keys():
        print >>f, t,
        print >>f, imei,
        print >>f, timeline_visible[t][imei]["all"],
        appnames = appname_mapping.keys()
        appnames.sort()
        for app in appnames:
            if app in timeline_visible[t][imei]:
                print >>f, timeline_visible[t][imei][app],
            else:
                print >>f, 0,

        print >>f
        
