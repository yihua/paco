#!/usr/bin/python

f = open("/z/user-study-imc15/PACO/gesture_summary.txt")

user_last_time = {}
user_time_distribution = {}



for line in f.readlines():
    line = line.split()
    user = line[0]
    clicktype = line[1]
    start_time = float(line[3])

    if clicktype not in ["Touch_Screen", "Menu_Touch_Key", "Back_Touch_Key"]:
        continue

    if user in user_last_time:

        delta = int(start_time - user_last_time[user])

        if delta > 1200:
            continue

        if user not in user_time_distribution:
            user_time_distribution[user] = {}

        if delta not in user_time_distribution[user]:
            user_time_distribution[user][delta] = 0
        user_time_distribution[user][delta] += 1
       
    user_last_time[user] = start_time

f = open("output_files/inter_click_validation.txt", "w")

for i in range(1200):
    for k, v in user_time_distribution.iteritems():
        if i in v:
            print >>f, v[i],
        else:
            print >>f, 0,
    print >>f
