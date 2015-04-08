import sys
import os.path

f_list = open('/nfs/beirut1/userstudy/2nd_round/userinput/filelist', 'r')

f_result = open('problem_userinput.txt', 'w')
f_notrace = open('problem_notrace.txt', 'w')

count = 0

for line in f_list:
    if (count % 1000 == 0):
        print "Processed: " + str(count)
    line = line.split('\n')[0]
    if (len(line) != 99):
        f_result.write(line + '\n')
    else:
        if not (os.path.isfile(line + '/oInputTrace')):
            #or os.path.isfile(line + '/oInputTrace.zip')):
            f_notrace.write(line + '\n')
    count += 1

f_list.close()
f_result.close()
f_notrace.close()
