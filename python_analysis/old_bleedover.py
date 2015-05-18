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


# when are they active
# find times within 1 minute of not being active

app_target_times = defaultdict(lambda: defaultdict(list))
app_foreground_times =  defaultdict(lambda: defaultdict(list))

user_started_apps = defaultdict(set)
user_pending_apps = defaultdict(lambda:defaultdict(int))
user_pending_foreground_apps = defaultdict(lambda:defaultdict(int))

user_last_time = defaultdict(int)
user_last_last_time = defaultdict(int)

limit = -1
#limit = 1000000
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

        if user_last_time[imei] != time:
           # print "NEW TIME:",  user_last_time[imei], time
            

            
            # resolve pending ones
            new_user_pending_apps = defaultdict(lambda:defaultdict(int))
            for appname in user_pending_apps[imei]:
                #print "\tcheck pending app", user_pending_apps[imei][appname], user_last_time[imei]
                if appname not in user_started_apps[imei] and user_pending_apps[imei][appname] != 0:
                    if user_pending_foreground_apps[imei][appname] != 0:
                        begin_time = user_pending_foreground_apps[imei][appname]
                        end_time = user_last_time[imei]
                        app_foreground_times[imei][appname].append([begin_time, end_time])
                        user_pending_foreground_apps[imei][appname] = 0

                    if user_last_time[imei] -  user_pending_apps[imei][appname] > 60000:
                        begin_time = user_pending_apps[imei][appname]
                        end_time = begin_time + 60000
                        #print "adding", appname, begin_time, end_time, user_pending_apps[imei][appname], user_last_time[imei]
                        app_target_times[imei][appname].append([begin_time, end_time])
                    else:
                        new_user_pending_apps[imei][appname] = user_pending_apps[imei][appname]
            user_pending_apps = new_user_pending_apps

            # new apps not pending
            for appname in user_started_apps[imei]:
                #print "\tpending app", user_pending_apps[imei][appname]
                if user_pending_apps[imei][appname] != user_last_last_time[imei]:
                    begin_time = user_pending_apps[imei][appname]
                    end_time = min(begin_time + 60000, user_last_time[imei])
                    if end_time - begin_time > 200:
                        print "adding", appname, begin_time, end_time, user_pending_apps[imei][appname], user_last_last_time[imei]
                        app_target_times[imei][appname].append([begin_time, end_time])
                    del user_pending_apps[imei][appname]

                user_pending_apps[imei][appname] = time 
                #print "\tnew pending app", user_pending_apps[imei][appname]
            user_started_apps[imei] = set()

        if is_foreground == "100" and appname in appname_mapping:
            #print "\tFOREGROUND:", imei, appname, time
            user_started_apps[imei].add(appname)
            if user_pending_foreground_apps[imei][appname] != 0:
                user_pending_foreground_apps[imei][appname] = time


        user_last_time[imei] = time

energy = c_session.CEnergy()
energy.load_data()
#energy.load_data(10000000)

app_times_pointers = defaultdict(lambda:defaultdict(int))
app_foreground_pointers = defaultdict(lambda:defaultdict(int))


#for user, v in app_target_times.iteritems():
#    for appname, v2 in v.iteritems():
#        for item in v2:
#            print user, appname, item

# data to save: amount of energy
bad_energy = defaultdict(float)
bad_data = defaultdict(float)
ok_energy = defaultdict(float)
ok_data = defaultdict(float)
good_energy = defaultdict(float)
good_data = defaultdict(float)

for item in energy.data:
    imei = item["userid"]
    app = item["process_name"]
    if app not in appname_mapping:
        continue
    ok_energy[app]  += item["energy"]
    ok_data[app] += (item["upbytes"] + item["downbytes"])

    time = int(item["timestamp"]*1000)

    times_to_examine = len( app_target_times[imei][app])
    times_to_examine_foreground = len( app_foreground_times[imei][app])

    
    if imei in app_foreground_times and app in app_foreground_times[imei] and len(app_foreground_times[imei][app]) > 0:
        
        pointer = app_foreground_pointers[imei][app]
        while pointer < times_to_examine and time > app_foreground_times[imei][app][pointer][1]:
            pointer += 1
            if pointer >= times_to_examine_foreground: 
                del app_foregroun_times[imei][app]
                break
        if pointer >= times_to_examine_foreground:
            if imei in app_target_times and app in  app_target_times[imei]: 
                del app_target_times[imei][app]
        elif not time < app_target_times[imei][app][pointer][0]:
            good_energy[app] += item["energy"]
            good_data[app] += (item["upbytes"] + item["downbytes"])


    if imei in app_target_times and app in app_target_times[imei] and len(app_target_times[imei][app]) > 0:
        pointer = app_times_pointers[imei][app]

        while pointer < times_to_examine and time > app_target_times[imei][app][pointer][1]:
            pointer += 1
            if pointer >= times_to_examine: 
                del app_target_times[imei][app]
                break

        if pointer >= times_to_examine:
            if imei in app_target_times and app in  app_target_times[imei]: 
                del app_target_times[imei][app]
            continue
#        print app, time, app_target_times[imei][app][pointer][0]
        if time < app_target_times[imei][app][pointer][0]:
            continue
        bad_energy[app] += item["energy"]
        bad_data[app] += (item["upbytes"] + item["downbytes"])
            
f = open("output_files/bleedover.txt", "w")
for app in bad_energy.keys():
    print >>f, app, bad_energy[app], bad_data[app], ok_energy[app], ok_data[app], good_data[app], good_energy[app]
f.close()
