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
        "com.sina.weibo.servant":"weibo",\
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
        "com.halfbrick.fruitninjafree":"fruitninja",\
        "com.urbanairship.push.process":"urbanairship",\
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
app_background_times =  defaultdict(lambda: defaultdict(list))

user_started_apps = defaultdict(set)
user_pending_apps = defaultdict(lambda:defaultdict(int))
user_pending_foreground_apps = defaultdict(lambda:defaultdict(int))
user_pending_background_apps = defaultdict(lambda:defaultdict(int))

user_last_time = defaultdict(int)
user_last_last_time = defaultdict(int)
user_last_state = defaultdict(lambda: defaultdict(str))

AFTER_TIME = 1800000

limit = -1
limit = 1000
#limit = 5771718
for name in dirs:
    f = open(name)
    print name
    for line in f:

        (imei, time, appname, is_foreground) = line.split()
        if appname != "com.android.chrome":
            continue
        print appname

        if limit != -1:
            if limit > 0:
                limit -= 1
            else:
                break

        time = int(time)

        if user_last_time[imei] != time:
            for appname in appname_mapping.keys():
                print "appname_mapping:", user_pending_foreground_apps[imei][appname], user_pending_background_apps[imei][appname], appname
                if user_pending_foreground_apps[imei][appname] != 0 and user_last_state[imei][appname] == "bg":
                    begin_time = user_pending_foreground_apps[imei][appname]
                    end_time = user_last_time[imei]
                    print "foreground", begin_time, end_time, imei, appname
                    app_foreground_times[imei][appname].append([begin_time, end_time])
                    user_pending_foreground_apps[imei][appname] = 0

                if user_pending_background_apps[imei][appname] != 0 and  user_last_state[imei][appname] == "fg":
                    begin_time = user_pending_background_apps[imei][appname]
                    end_time = user_last_time[imei]
                    print "background", begin_time, end_time, imei, appname
                    app_background_times[imei][appname].append([begin_time, end_time])
                    user_pending_background_apps[imei][appname] = 0

            print "NEW TIME:",  user_last_time[imei], time
            
            # resolve pending ones
            new_user_pending_apps = defaultdict(lambda:defaultdict(int))
            for appname in user_pending_apps[imei]:
                print "\tcheck pending app", user_pending_apps[imei][appname], user_last_time[imei]
                if appname not in user_started_apps[imei] and user_pending_apps[imei][appname] != 0:

                    if user_last_time[imei] -  user_pending_apps[imei][appname] > AFTER_TIME:
                        begin_time = user_pending_apps[imei][appname]
                        end_time = begin_time + AFTER_TIME 
                        print "adding", appname, begin_time, end_time, user_pending_apps[imei][appname], user_last_time[imei]
                        app_target_times[imei][appname].append([begin_time, end_time])
                    else:
                        new_user_pending_apps[imei][appname] = user_pending_apps[imei][appname]
            user_pending_apps = new_user_pending_apps

            # new apps not pending
            for appname in user_started_apps[imei]:
                print "\tpending app", user_pending_apps[imei][appname]
                if user_pending_apps[imei][appname] != user_last_last_time[imei]:
                    begin_time = user_pending_apps[imei][appname]
                    end_time = min(begin_time + AFTER_TIME, user_last_time[imei])
                    if end_time - begin_time > 200:
                        print "adding", appname, begin_time, end_time, user_pending_apps[imei][appname], user_last_last_time[imei]
                        app_target_times[imei][appname].append([begin_time, end_time])
                    del user_pending_apps[imei][appname]

                user_pending_apps[imei][appname] = time 
                #print "\tnew pending app", user_pending_apps[imei][appname]
            user_started_apps[imei] = set()

        if is_foreground == "100" and appname in appname_mapping:
#            print "\tFOREGROUND:", imei, appname, time
            user_started_apps[imei].add(appname)


        if (is_foreground == "100" or is_foreground == "200") and appname in appname_mapping:
            if user_pending_foreground_apps[imei][appname] == 0:
                #print "\tForeground:", imei, appname, time
                user_pending_foreground_apps[imei][appname] = time
            user_last_state[imei][appname] = "fg"

        if (is_foreground == "400" or is_foreground == "130" or is_foreground == "300" ) and appname in appname_mapping:
            if user_pending_background_apps[imei][appname] == 0:
                print "\tBACKGROUND:", imei, appname, time
                user_pending_background_apps[imei][appname] = time
            user_last_state[imei][appname] = "bg"


        user_last_time[imei] = time

#    print len(app_target_times), len(app_foreground_times), len(app_background_times) 

exit() # XXX
limit = -1
#limit = 10000000
energy = c_session.CEnergy()
energy.load_data(limit)

#energy.load_data(10000000)
print "Loaded energy"

app_times_pointers = defaultdict(lambda:defaultdict(int))
app_foreground_pointers = defaultdict(lambda:defaultdict(int))
app_background_pointers = defaultdict(lambda:defaultdict(int))


#for user, v in app_target_times.iteritems():
#    for appname, v2 in v.iteritems():
#        for item in v2:
#            print user, appname, item

# data to save: amount of energy
bad_energy = defaultdict(float)
bad_data = defaultdict(float)

all_energy = defaultdict(float)
all_data = defaultdict(float)

good_energy = defaultdict(float)
good_data = defaultdict(float)

background_energy = defaultdict(float)
background_data = defaultdict(float)

bad_energy_today = defaultdict(float)
bad_data_today = defaultdict(float)

all_energy_today = defaultdict(float)
all_data_today = defaultdict(float)

good_energy_today = defaultdict(float)
good_data_today = defaultdict(float)

background_energy_today = defaultdict(float)
background_data_today = defaultdict(float)

total_energy_today = 0
total_data_today = 0

f = open("output_files/energy_by_time_direct_by_day.txt", "w")

last_day = None

for item in energy.data:
    imei = item["userid"]
    app = item["process_name"]
    total_energy_today += item["energy"]
    total_data_today  += (item["upbytes"] + item["downbytes"])

    if app not in appname_mapping:
        continue

    time = int(item["timestamp"]*1000)
    day = int(time/(1000*24*3600))

    times_to_examine = len( app_target_times[imei][app])
    times_to_examine_foreground = len( app_foreground_times[imei][app])
    times_to_examine_background = len( app_background_times[imei][app])
  
    if day != last_day and last_day != None:

        print "Analyzing day:", last_day

        for app in all_energy_today.keys():
            print >>f, day, app, 
            if app in bad_energy_today:
                print >>f, bad_energy[app], bad_data[app], 
            else:    
                print >>f, 0, 0,
            if app in all_energy_today:
                print >>f, all_energy[app], all_data[app], 
            else:    
                print >>f, 0, 0,
            if app in good_energy_today:
                print >>f, good_energy[app], good_data[app], 
            else:    
                print >>f, 0, 0,
            if app in background_energy_today:
                print >>f, background_energy[app], background_data[app], 
            else:    
                print >>f, 0, 0,
            print >>f

        print >>f, day, "TOTAL", total_energy_today, total_data_today

        f.flush()

        bad_energy_today = defaultdict(float)
        bad_data_today = defaultdict(float)
        all_energy_today = defaultdict(float)
        all_data_today = defaultdict(float)
        good_energy_today = defaultdict(float)
        good_data_today = defaultdict(float)
        background_energy_today = defaultdict(float)
        background_data_today = defaultdict(float)
        total_energy_today = 0
        total_data_today = 0

    last_day = day

    all_energy[app]  += item["energy"]
    all_data[app] += (item["upbytes"] + item["downbytes"])
    all_energy_today[app]  += item["energy"]
    all_data_today[app] += (item["upbytes"] + item["downbytes"])
        

#    if imei == "353091053665792":
#        print app
    if imei in app_foreground_times and app in app_foreground_times[imei] and len(app_foreground_times[imei][app]) > 0:
#        print "here" 
        pointer = app_foreground_pointers[imei][app]

        while pointer < len(app_foreground_times[imei][app]) and time > app_foreground_times[imei][app][pointer][1]:
            pointer += 1
            if pointer >= times_to_examine_foreground: 
                del app_foreground_times[imei][app]
                times_to_examine_foreground = len(app_foreground_times[imei][app])
                break

        if pointer >= times_to_examine_foreground:
            if imei in app_foreground_times and app in  app_foreground_times[imei]: 
                del app_foreground_times[imei][app]
                times_to_examine_foreground = len(app_foreground_times[imei][app])
            continue
        elif pointer < len(app_foreground_times[imei][app]) and not time < app_foreground_times[imei][app][pointer][0]:
            good_energy[app] += item["energy"]
            good_data[app] += (item["upbytes"] + item["downbytes"])
            good_energy_today[app] += item["energy"]
            good_data_today[app] += (item["upbytes"] + item["downbytes"])
        app_foreground_pointers[imei][app] = pointer

    if imei in app_background_times and app in app_background_times[imei] and len(app_background_times[imei][app]) > 0:
#        print "here" 
        pointer = app_background_pointers[imei][app]
        while pointer < len(app_background_times[imei][app]) and time > app_background_times[imei][app][pointer][1]:
            pointer += 1
            if pointer >= times_to_examine_background: 
                times_to_examine_background = len(app_background_times[imei][app])
                break
        if pointer >= times_to_examine_background:
            if imei in app_background_times and app in  app_background_times[imei]: 
                times_to_examine_background = len(app_background_times[imei][app])
            continue
        elif pointer < len(app_background_times[imei][app]) and not time < app_background_times[imei][app][pointer][0]:
            background_energy[app] += item["energy"]
            background_data[app] += (item["upbytes"] + item["downbytes"])
            background_energy_today[app] += item["energy"]
            background_data_today[app] += (item["upbytes"] + item["downbytes"])
        app_background_pointers[imei][app] = pointer

    if imei in app_target_times and app in app_target_times[imei] and len(app_target_times[imei][app]) > 0:
        pointer = app_times_pointers[imei][app]
        while pointer < len(app_target_times[imei][app]) and time > app_target_times[imei][app][pointer][1]:
            pointer += 1
            if pointer >= times_to_examine: 
                times_to_examine = len(app_target_times[imei][app])

                break

        app_times_pointers[imei][app] = pointer
        if pointer >= times_to_examine:
            if imei in app_target_times and app in  app_target_times[imei]: 
                times_to_examine = len(app_target_times[imei][app])
            continue

#        print app, time, app_target_times[imei][app][pointer][0]
        try: 
            app_target_times[imei][app][pointer][0]
        except:
            print "error!", imei, app, pointer, len( app_target_times[imei][app]), app_target_times[imei][app]
            continue

        if pointer > len(app_target_times[imei][app]) or time < app_target_times[imei][app][pointer][0]:
#            print time,  app_target_times[imei][app][pointer][0],  time < app_target_times[imei][app][pointer][0]
            continue
#        print "here"
        bad_energy[app] += item["energy"]
        bad_data[app] += (item["upbytes"] + item["downbytes"])

        bad_energy_today[app] += item["energy"]
        bad_data_today[app] += (item["upbytes"] + item["downbytes"])
f.close()

f = open("output_files/energy_by_time_direct_2.txt", "w")
for app in bad_energy.keys():
    print >>f, app, bad_energy[app], bad_data[app], all_energy[app], all_data[app], good_data[app], good_energy[app], background_data[app], background_energy[app]
f.close()
