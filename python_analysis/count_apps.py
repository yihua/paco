#!/usr/bin/python

from collections import defaultdict
from scipy.stats.stats import pearsonr

import operator
import c_session

import numpy
import parse_wifi

flows = c_session.CFlow()

flows.load_data()

userids = set()
apps = set()
times = set()
for item in flows.data:
    userid = item["userID"]
    app = item["app_name"].split(":")[0]
    time = int(item["start_time"])/(24*3600)
    userids.add(userid)
    times.add(time)
    apps.add(app)
print "num apps", len(apps)
print "num userids", len(userids)
print "num days", len(times)
