import sys
import io

def compare(a, b):
    if (a == b):
        return True
    else:
        return False

f_power = open('/z/user-study-imc15/PACO/energy_summary.txt', 'r')

users = {}
users_aggr = {}

start_time = 1356152400.0

period = 60*60*24.0

count = 0

for line in f_power:
    if (count % 100000 == 0):
        print "Processed: " + str(count)
    #if (count > 3000):
    #    break
    count += 1
    line = line.split()
    line[1] = line[1].replace('/', '-')
    if (float(line[2]) < start_time):
        continue
    if not (line[0] in users):
        users[line[0]] = {}
    if not (line[0] in users_aggr):
        users_aggr[line[0]] = [[start_time, 0.0, 0.0, 0.0, 0.0]]
    if not (line[1] in users[line[0]]):
        users[line[0]][line[1]] = [[start_time,0.0,0.0, 0.0, 0.0]] # time energy-active energy-passive

    if (float(line[2]) < start_time + period):
        #users[line[0]][line[1]][-1][0] = start_time
        if (float(line[3]) >= 0):
            users[line[0]][line[1]][-1][3] += float(line[4])
            users[line[0]][line[1]][-1][4] += float(line[5])
            users_aggr[line[0]][-1][3] += float(line[4])
            users_aggr[line[0]][-1][4] += float(line[5])
            if (int(line[4]) + int(line[5]) > 0):
                if not (compare(users[line[0]][line[1]][-1][0], start_time) and
                        compare(users_aggr[line[0]][-1][0], start_time)):
                    print "************** Time Error **************"
                users[line[0]][line[1]][-1][1] += float(line[3])
                users_aggr[line[0]][-1][1] += float(line[3])
            else:
                if not (compare(users[line[0]][line[1]][-1][0], start_time) and
                        compare(users_aggr[line[0]][-1][0], start_time)):
                    print "************** Time Error **************"
                users[line[0]][line[1]][-1][2] += float(line[3])
                users_aggr[line[0]][-1][2] += float(line[3])
        else:
            print "-------------- Energy error --------------", line
    else:
        print 'trigger:', start_time
        while (float(line[2]) > start_time + period):
            start_time += period
            for user in users:
                users_aggr[user].append([start_time, 0.0, 0.0,0.0,0.0])
                for appname in users[user]:
                    users[user][appname].append([start_time,0.0,0.0,0.0,0.0])
        #users[line[0]][line[1]][-1][0] = start_time
        if (float(line[3]) >= 0):
            users[line[0]][line[1]][-1][3] += float(line[4])
            users[line[0]][line[1]][-1][4] += float(line[5])
            users_aggr[line[0]][-1][3] += float(line[4])
            users_aggr[line[0]][-1][4] += float(line[5])
            if (int(line[4]) + int(line[5]) > 0):
                if not (compare(users[line[0]][line[1]][-1][0], start_time) and
                        compare(users_aggr[line[0]][-1][0], start_time)):
                    print "************** Time Error **************"
                users[line[0]][line[1]][-1][1] += float(line[3])
                users_aggr[line[0]][-1][1] += float(line[3])
            else:
                if not (compare(users[line[0]][line[1]][-1][0], start_time) and
                        compare(users_aggr[line[0]][-1][0], start_time)):
                    print "************** Time Error **************"
                users[line[0]][line[1]][-1][2] += float(line[3])
                users_aggr[line[0]][-1][2] += float(line[3])
        else:
            print "-------------- Energy error --------------", line

    #print users[line[0]][line[1]][-1][1]
    if (users[line[0]][line[1]][-1][1] < 0):
        print "############# warning ##################"
        print line[0], line[1]
f_power.close()
#print users 
for user in users:
    f_app = open('/z/user-study-imc15/PACO/result/' + user, 'w')
    for i in range(len(users_aggr[user])):
        f_app.write(str(users_aggr[user][i][0]) + '\t' + str(users_aggr[user][i][1])
                        + '\t' + str(users_aggr[user][i][2])
                        + '\t' + str(users_aggr[user][i][3])
                        + '\t' + str(users_aggr[user][i][4]))
        if (users_aggr[user][i][3] + users_aggr[user][i][4] > 0):
            f_app.write('\t' + str((users_aggr[user][i][1] + users_aggr[user][i][2])/(users_aggr[user][i][3]+users_aggr[user][i][4])) + '\n')
        else:
            f_app.write('\t0.0\n')
    f_app.close()
    for appname in users[user]:
        f_app = open('/z/user-study-imc15/PACO/result/' + user + '-' + appname, 'w')
        if (len(users[user][appname]) == 0):
            continue
        for i in range(len(users[user][appname])):
            f_app.write(str(users[user][appname][i][0]) + '\t' + str(users[user][appname][i][1])
                        + '\t' + str(users[user][appname][i][2])
                        + '\t' + str(users[user][appname][i][3])
                        + '\t' + str(users[user][appname][i][4]))
            if (users[user][appname][i][3] + users[user][appname][i][4] > 0):
                f_app.write('\t' + str((users[user][appname][i][1] + users[user][appname][i][2])/(users[user][appname][i][3]+users[user][appname][i][4])) + '\n')
            else:
                f_app.write('\t0.0\n')
        f_app.close()
