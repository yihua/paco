import os, sys

#findex=sys.argv[1]

active={}
BG=[130,300,400]
FG=[100,200]
imea=-1
time=-1
#filein_active=open('/home/ashnik/active_data/active20'+findex, 'r')

files = ["active_sorted_201210",  "active_sorted_201212", "active_sorted_201301", "active_sorted_201302", "active_sorted_201303", "active_sorted_201304", "active_sorted_201305", "active_sorted_201306", "active_sorted_201307", "active_sorted_201308", "active_sorted_201309", "active_sorted_201310", "active_sorted_201311", "active_sorted_201312", "active_sorted_201401", "active_sorted_201402", "active_sorted_201403", "active_sorted_201404", "active_sorted_201405", "active_sorted_201406", "active_sorted_201407",  "active_sorted_201408"]

for f in files:

    print "parsing file", f

    filein_active=open('/nfs/beirut2/ashnik/active_data/' + f, 'r')
    for line in filein_active:
        toks=line.strip().split(' ')
        app=""
        imea=-1
        if len(toks)==3 and len(toks[0])==15 and len(toks[2])==3:
            imea=toks[0]
            code=int(toks[2])
            app=toks[1]
        elif len(toks)==4 and len(toks[0])==15 and len(toks[1])==13 and len(toks[3])==3:
            imea=toks[0]
            time=long(toks[1])
            app=toks[2]
            code=int(toks[3])
            if code in FG:
                code=100
            elif code in BG:
                code=400
        if imea!=-1 and app!="" and time!=-1 and code in [100,130,200,300,400]:
            if not imea in active:
                active[imea]={}
            if not app in active[imea]:
                active[imea][app]=[]
            if len(active[imea][app])!=0:
                if active[imea][app][-1][1]!=code:
                    active[imea][app].append((time, code))
            else:
                active[imea][app].append((time, code)) 
imea=-1
time=-1

f = open("output_files/bleedover_intermediate.txt", "w")

limit = 1000000
filein_packet = open('../energy_summary.txt') 
for line in filein_packet:
    if limit == 0:
        break
    elif limit > 0:
        limit -= 1


	line=line.split()
                
    imea = line[0]
    app = line[1]
    time = int(float(line[2])*1000)
    energy = float(line[3])
    data = int(line[4]) + int(line[5])

#	print '***',line
    if not imea in active:
        continue
    if not app in active[imea]:
        continue
    l=active[imea][app]
    i=0
    for i  in range(0, len(l)):
        if i!=len(l)-1:
            t=l[i][0]
            nt=l[i+1][0]
            if time>=t and time<nt:
                if l[i][1]==400:
                    print >>f, imea, app, data, energy, time, t, nt 
                break
        else:
            t=l[i][0]
            if l[i][1]==400 and time>=t:
                print >>f, imea, app, data, energy, time, t



		

			

