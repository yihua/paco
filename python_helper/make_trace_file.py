#!/usr/bin/python

import glob

# Generate a complete list of user study data and feed into the trace file

root_dir = "/nfs/beirut1/userstudy/2nd_round/"
file_limit = 200 # optional, set to -1 if not needed

# Note: if for some reason someone is using this in 2020 it will break :)
candidate_dirs = glob.glob(root_dir + "201*/141*/imap*/traffic.cap*")

f = open("./pcaplistallsort", "w")


for item in candidate_dirs:
	file_limit -= 1
	print >> f, item

	if file_limit == 0:
		break
