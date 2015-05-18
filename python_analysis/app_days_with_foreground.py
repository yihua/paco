#!/usr/bin/python

from collections import defaultdict
import operator
import glob
import numpy

appnames = ["com.google.android.apps.plus", "com.sina.weibo.servant", "com.google.android.apps.maps", "com.weather.Weather", "com.espn.score_center", "com.twitter.android", "com.instagram.android", "com.facebook.katana", "com.urbanairship.push.process"]

# names = ["plus", "weibo", "maps", "weather", "espn", "twitter", "instagram", "facebook", "urbanairship"]


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

app_is_foreground = defaultdict(lambda:defaultdict(set))

g = open("output_files/app_days_with_foreground.txt", "w")
for name in dirs:
    f = open(name)
    print name
    for line in f:
        (imei, time, appname, is_foreground) = line.split()
        appname = appname.split(":")[0]
        if appname not in appnames:
            continue
        is_foreground = (is_foreground == "100")# or is_foreground =="200")

        day =  int(time)/(3600*1000*24)
        if is_foreground:
            if day not in app_is_foreground[imei][appname]:
                print >>g, imei, appname, day, time
            app_is_foreground[imei][appname].add(day)
g.close()
