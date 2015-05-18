#!/usr/bin/python 

from collections import defaultdict

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

#f = open("/nfs/beirut2/ashnik/merge/allbg")
f = open("output_files/bleedover_intermediate.txt")

data_above_60 = 0
data_below_60 = 0
energy_above_60 = 0
energy_below_60 = 0

data_above_by_app = defaultdict(int)
data_below_by_app = defaultdict(int)

energy_above_by_app = defaultdict(int)
energy_below_by_app = defaultdict(int)


bg_time_60 = defaultdict(int)
bg_time = defaultdict(int)

appnames = appname_mapping.keys()

time_tuples = defaultdict(lambda:defaultdict(None))

last_energy_all = defaultdict(lambda:defaultdict(int))
last_energy = defaultdict(lambda:defaultdict(int))



minbins = [0 for i in range(120)]
minbins_data = [0 for i in range(120)]

limit = -1 #10000
#limit = 10000000
for line in f:

    line = line.split()

    if limit > 0:
        limit -= 1
    elif limit == 0:
        break

    appname = line[1].split(":")[0]
    userid = line[0]

    data = int(line[2])
    energy = float(line[3])
    begin_time = int(line[5])
    cur_time = int(line[4])


    delta = cur_time - begin_time 
    if delta > 60000:
        data_above_60 += data
#        if appname in appnames:
        data_above_by_app[appname] += data 
        last_energy[appname][userid] += energy

    elif delta > 0:
        data_below_60 += data 
#        if appname in appnames:
        data_below_by_app[appname] += data 
        last_energy_all[appname][userid] += energy

    min_delta = int(delta/60000)
    if min_delta < 120:
        add_energy = energy
#        print energy
        if delta < 10000:
            add_energy -= 1.06
        minbins[min_delta] += max(add_energy, 0)
        minbins_data[min_delta] += data 


    if len(line) > 6 and (userid not in time_tuples or appname not in time_tuples[userid] or time_tuples[userid][appname][0] != line[5] or time_tuples[userid][appname][1] != line[6]):
        try:
            t = int(line[6]) - int(line[5])
        except:
            print "error", line
            continue
        bg_time[appname] += t 
        bg_time_60[appname] += min(t, 60000) 
        time_tuples[userid][appname] = (line[5], line[6])

        if appname in last_energy_all and userid in last_energy_all[appname]:
            if last_energy_all[appname][userid] - 10> 0:
                energy_above_by_app[appname] += (last_energy_all[appname][userid]-10)

        if appname in last_energy and userid in last_energy[appname]:
            if last_energy[appname][userid] - 10> 0:
                energy_below_by_app[appname] += (last_energy[appname][userid]-10)


print data_below_60/float(data_above_60 + data_below_60)
    # 353091053685444 com.appztastic.snapchatsavepics 0 1388553592256 1389966681501

for appname in data_below_by_app.keys():
#    try:
        if data_below_by_app[appname] + data_above_by_app[appname] > 0:
            fraction_data = data_below_by_app[appname]/float(data_below_by_app[appname] + data_above_by_app[appname])
        else:
            fraction_data = 0

        if bg_time[appname] > 0:
            fraction_time = bg_time_60[appname]/float(bg_time[appname])
        else:
            fraction_time = 1 

        if energy_below_by_app[appname] + energy_above_by_app[appname]> 0: 
            fraction_energy = energy_below_by_app[appname]/float(energy_below_by_app[appname] + energy_above_by_app[appname])
        else:
            fraction_energy = 0

        print appname, fraction_data, fraction_energy, fraction_data/fraction_time, fraction_energy/fraction_time

#    except:
#        continue

f = open("background_data_energy_by_time.dat", "w")
for i in range(120):
    print >>f, i, minbins[i], minbins_data[i]
