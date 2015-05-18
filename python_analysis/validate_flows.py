#!/usr/bin/python

from collections import defaultdict
f = open("/z/user-study-imc15/PACO/flow_summary.txt")

userid_count = defaultdict(int)
userid_count_bad = defaultdict(int)

for line in f.readlines():
    line = line.split(" ")
    try:
        userid = line[0]
        mapping = line[13]
    except:
        print line
        continue
    if "400:" in mapping or "500:" in mapping or "100:" in mapping or "130:" in mapping or "300:" in mapping or "200:" in mapping:
        userid_count[userid] += 1
    else:
        userid_count_bad[userid] += 1

users = set(userid_count.keys())
users.update(set(userid_count_bad.keys()))

for user in users:
    print user,
    if user in userid_count:
        print userid_count[user],
    else:
        print 0,
    if user in userid_count_bad:
        print userid_count_bad[user],
    else:
        print 0,

    print
