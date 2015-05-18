#!/usr/bin/python

PRINT_JUMP = 10

########################   Attributes in aggregate #######################
f = open("plot_encryption_usage_trends.p", "w")

print >>f,  "set term png"
print >>f,  "set output \"encryption_usage_trends.png\""
print >>f,  "set title \"Overall data usage trends\""
print >>f,  "set ylabel \"Total amount of traffic, bytes\""
print >>f,  "set xlabel \"Day\""
print >>f,  "set logscale y"

args = [str(x) for x in range(2,PRINT_JUMP+2,2)]
args = "+$".join(args)

title = "\"unencrypted, up\""

print >>f,  "plot \"hosts.txt\" using 1:($" + args + ") w lines t " + title,

args = [str(x) for x in range(3,PRINT_JUMP + 3,2)]
args = "+$".join(args)

title = "\"encrypted, up\""

print >>f,  ", \"\" using 1:($" + args + ") w lines t " + title,

args = [str(x) for x in range(PRINT_JUMP+2,PRINT_JUMP*2+2,2)]
args = "+$".join(args)

title = "\"unencrypted, down\""

print >>f,  ", \"\" using 1:($" + args + ") w lines t " + title,

args = [str(x) for x in range(PRINT_JUMP+3,PRINT_JUMP*2+3,2)]
args = "+$".join(args)

title = "\"encrypted, down\""

print >>f,  ", \"\" using 1:($" + args + ") w lines t " + title
f.close()

########################  Data, top N #######################

f = open("hosts.txt", "r")

labels = f.readline()
labels = labels.split()
f.close()

f = open("app_data_trends_up.p", "w")
g = open("app_data_trends_up_encrypt.p", "w")
h = open("app_data_trends_down.p", "w")
e = open("app_data_trends_down_encrypt.p", "w")

print >>f,  "set term png"
print >>f,  "set output \"app_data_trends_up.png\""
print >>f,  "set title \"Per-app data usage trends, upload\""
print >>f,  "set ylabel \"Total amount of traffic, bytes\""
print >>f,  "set xlabel \"Day\""
print >>f,  "set logscale y"

print >>g,  "set term png"
print >>g,  "set output \"app_data_trends_up_encrypt.png\""
print >>g,  "set title \"Per-app data usage trends, upload, encrypted\""
print >>g,  "set ylabel \"Total amount of traffic, bytes\""
print >>g,  "set xlabel \"Day\""
print >>g,  "set logscale y"

print >>h,  "set term png"
print >>h,  "set output \"app_data_trends_down.png\""
print >>h,  "set title \"Per-app data usage trends, download\""
print >>h,  "set ylabel \"Total amount of traffic, bytes\""
print >>h,  "set xlabel \"Day\""
print >>h,  "set logscale y"

print >>e,  "set term png"
print >>e,  "set output \"app_data_trends_down_encrypt.png\""
print >>e,  "set title \"Per-app data usage trends, download, encrypted\""
print >>e,  "set ylabel \"Total amount of traffic, bytes\""
print >>e,  "set xlabel \"Day\""
print >>e,  "set logscale y"

print labels
label = "\"" + labels[0][1:] + "\""
print label
print >>f,  "plot \"hosts.txt\" using 1:2 w lines t " + label,
print >>g,  "plot \"hosts.txt\" using 1:3 w lines t " + label,
print >>h,  "plot \"hosts.txt\" using 1:"+ str(PRINT_JUMP*2 + 2) +  " w lines t " + label,
print >>e,  "plot \"hosts.txt\" using 1:" + str(PRINT_JUMP*2 + 3) + " w lines t " + label,
for i in range(1,10):


    label = "\"" + labels[i] + "\""
    print >>f,  ", \"\" using 1:" + str(i*2+2) + "  w lines t " + label, 
    print >>g,  ", \"\" using 1:" + str(i*2+3) + " w lines t " + label, 
    print >>h,  ", \"\" using 1:" + str(i*2+PRINT_JUMP*2+2) + " w lines t " + label, 
    print >>e,  ", \"\" using 1:" + str(i*2+PRINT_JUMP*2+3) + " w lines t " + label, 

f.close()
g.close()
h.close()
e.close()
