#!/usr/bin/python

import c_session
import timeline
from collections import defaultdict
from IPy import IP
import socket
import operator
import sys
import argparse
import numpy

limit = -1 
#limit = 10000

parser = argparse.ArgumentParser()
parser.add_argument('--top_hosts', action='store_true')
parser.add_argument('--top_hosts_energy', action='store_true')
parser.add_argument('--top_hosts_data_to_energy', action='store_true')
parser.add_argument('--top_hosts_data_to_energy_overall', action='store_true')
parser.add_argument('--user_by_time', action='store_true')
parser.add_argument('--user_by_host', action='store_true')
parser.add_argument('--content', action='store_true')
parser.add_argument('--host_user_distribution', action='store_true')
args = parser.parse_args()

if not args.top_hosts \
        and not args.top_hosts_energy \
        and not args.top_hosts_data_to_energy \
        and not args.top_hosts_data_to_energy_overall \
        and not args.user_by_time \
        and not args.user_by_host \
        and not args.content \
        and not args.host_user_distribution:
    print "Error: no option!"
    exit()

flows = c_session.CFlow()
flows.load_data(limit)

timeline = timeline.TimeLine()

timestamp_adjustor = 3600 * 24 * 7

dns_lookup = {}

for item in flows.data:

    timeline.add_flow_item(item, timestamp_adjustor)

#    app = app.split(":")[0]
#    is_ip = False 
#    try:
#        # will throw an exception if not an IP
#        IP(app)
#        is_ip = True
#    except:
#        pass
#
#    if is_ip:
#        if app not in dns_lookup:
#            try:
#                host = socket.gethostbyaddr(app)[0]
#            except:
#                print "WARNING! failed to look up", app
#                continue
#            dns_lookup[app] = host
#            app = host
#        else:
#            app = dns_lookup[app]
#    
#    if "espn" in app:
#        app = "espn"
#    if "facebook" in app:
#        app = "facebook"
#
#    app = app.split(".")
#    if len(app) >= 3 and (app[-2] == "com" or app[-2] == "co"):
#        app = ".".join(app[-3:])
#    elif len(app) >= 2:
#        app = ".".join(app[-2:])
#    elif app != "espn" and app != "facebook":
#        continue

    # TODO encrypted or not encrypted

timeline.sync_to_database()

hours = timeline.fetch_all_hours()



#################################################################################
#   Get top hosts for downloads
#################################################################################

if args.top_hosts:
    top_downloads = defaultdict(int) 
    top_uploads = defaultdict(int) 
    top_everything = defaultdict(int)
    for hour in hours:
        host_ratings_up = defaultdict(int) 
        host_ratings_down = defaultdict(int)
        for row in timeline.fetch_data(["app"], hour):

            (bandwidth_up, bandwidth_down, bandwidth_up_encrypted, bandwidth_down_encrypted, host) = row

#            host_ratings_up[host] += bandwidth_up
#            host_ratings_down[host] += bandwidth_down
#            host_ratings_up[host] += bandwidth_up_encrypted
#            host_ratings_down[host] += bandwidth_down_encrypted

            top_uploads[host] += bandwidth_up
            top_downloads[host] += bandwidth_down
            top_uploads[host] += bandwidth_up_encrypted
            top_downloads[host] += bandwidth_down_encrypted

            top_everything[host] += (bandwidth_up + bandwidth_down + bandwidth_up_encrypted + bandwidth_down_encrypted)

#        host_ratings_keys = sorted(host_ratings_up.items(), key=operator.itemgetter(1))
#        for i in range(min(5, len(host_ratings_keys))):
#        for i in range(len(host_ratings_keys)):
#            key = host_ratings_keys[i][0]
#            top_uploads[key] += host_ratings_up[key]

#        host_ratings_keys = sorted(host_ratings_down.items(), key=operator.itemgetter(1))
#        for i in range(min(5, len(host_ratings_keys))):
#        for i in range(len(host_ratings_keys)):
#            top_downloads[key] += host_ratings_down[key]

#    keys_up = top_uploads.keys()
#    keys_up.sort()
#    keys_down = top_downloads.keys()
#    keys_down.sort()

    keys_up = sorted(top_uploads.items(), key=operator.itemgetter(1), reverse=True)
    keys_down = sorted(top_downloads.items(), key=operator.itemgetter(1), reverse=True)
    keys_all = sorted(top_everything.items(), key=operator.itemgetter(1), reverse=True)
    print keys_all

    f = open("output_files/top_upload_hosts.txt", "w")
    g = open("output_files/top_download_hosts.txt", "w")
    h = open("output_files/top_total_hosts.txt", "w")
    for i in range(100):
        if i < len(keys_up):
            print >>f, keys_up[i][0], keys_up[i][1]
        if i < len(keys_down):
            print >>g, keys_down[i][0], keys_down[i][1]
        if i < len(keys_all):
            print >>h, keys_all[i][0], keys_all[i][1]

    f.close()
    g.close()
    h.close()


#################################################################################
#   users with top hosts
#################################################################################

if args.host_user_distribution:
    f = open("output_files/top_upload_hosts.txt")
    upload_hosts = {} 
    key_order_up = []
    limit = 10
    for line in f:
        line = line.split()[0]
        upload_hosts[line] = 0 
        key_order_up.append(line)
        limit -= 1
        if limit == 0:
            break
    f.close()

    f = open("output_files/top_download_hosts.txt")
    key_order_down = []
    download_hosts = {} 
    limit = 10
    for line in f:
        line = line.split()[0]
        download_hosts[line] = 0 
        key_order_down.append(line)
        limit -= 1
        if limit == 0:
            break
    f.close()


    downloads_users = {}    
    uploads_users = {}    

    f = open("output_files/popular_app_distribution.txt", "w")
#    key_order_down = download_hosts.keys()
    print >>f,  " ".join(key_order_down),
#    key_order_up = upload_hosts.keys()

    top_uploads = {}
    top_downloads = {}
   
    users = set()

    for hour in hours:
        for row in timeline.fetch_data_averages(["app", "userid"], hour):

            (bandwidth_up, bandwidth_down, bandwidth_up_encrypted, \
                    bandwidth_down_encrypted, host, user) = row

            users.add(user)

            if user not in downloads_users:
                downloads_users[user] = dict(download_hosts)
                uploads_users[user] = dict(upload_hosts)

                top_uploads[user] = defaultdict(int)
                top_downloads[user] = defaultdict(int)

            top_uploads[user][host] += bandwidth_up
            top_downloads[user][host] += bandwidth_down
            top_uploads[user][host] += bandwidth_up_encrypted
            top_downloads[user][host] += bandwidth_down_encrypted

#            if host in download_hosts:
#                download_hosts[host][user] += bandwidth_down
#                download_hosts[host][user] += bandwidth_down_encrypted
#            if host in upload_hosts:
#                upload_hosts[host][user] += bandwidth_up
#                upload_hosts[host][user] += bandwidth_up_encrypted

    for user in users:
        print >>f, user,
        for k in key_order_down:
            if k in top_downloads[user]:
                print >>f, top_downloads[user][k],
            else:
                print >>f, 0,
        for k in key_order_up:
            if k in top_uploads[user]:
                print >>f, top_uploads[user][k],
            else:
                print >>f, 0,
        print >>f
    f.close()

    f = open("output_files/top_apps_by_user.txt", "w")
    for user in top_uploads.keys():

        print >>f, "=========================================="
        print >>f, user
        print >>f, "=========================================="

        keys_up = sorted(top_uploads[user].items(), key=operator.itemgetter(1), reverse=True)
        keys_down = sorted(top_downloads[user].items(), key=operator.itemgetter(1), reverse=True)
        for i in range(10):
            if i < len(keys_up):
                print >>f, keys_up[i][0], keys_up[i][1]
        print >>f, "=========================================="
        for i in range(10):
            if i < len(keys_down):
                print >>f, keys_down[i][0], keys_down[i][1]


#################################################################################
#   Find top energy users 
#################################################################################


if args.top_hosts_energy:
    top_energy = defaultdict(float)
    for hour in hours:
        for row in timeline.fetch_data(["app"], hour):
            (bandwidth_up, bandwidth_down, bandwidth_up_encrypted, \
                    bandwidth_down_encrypted, energy_wifi, \
                    energy_cellular, energy_per_byte_cellular, \
                    energy_per_byte_wifi, host) = row
            top_energy[host] += (energy_wifi + energy_cellular)

    keys = sorted(top_energy.items(), key=operator.itemgetter(1), reverse=True)
    f = open("output_files/top_energy_hosts.txt", "w")
    for i in range(100):
        if i < len(keys):
            print >>f, keys[i][0], keys[i][1]
    f.close()

#################################################################################
#   Find top data to energy ratio
#################################################################################


if args.top_hosts_data_to_energy:
    top_energy = defaultdict(float)
    for hour in hours:
        for row in timeline.fetch_data(["app"], hour):
            (bandwidth_up, bandwidth_down, bandwidth_up_encrypted, \
                    bandwidth_down_encrypted, energy_wifi, \
                    energy_cellular, energy_per_byte_cellular, \
                    energy_per_byte_wifi, host) = row
            if float(bandwidth_up +  bandwidth_down) > 0:
                top_energy[host] += float(energy_wifi + energy_cellular)/float(bandwidth_up +  bandwidth_down)

    keys = sorted(top_energy.items(), key=operator.itemgetter(1), reverse=True)
    f = open("output_files/top_energy_ratio_hosts.txt", "w")
    for i in range(len(keys)):
        if i < len(keys):
            print >>f, keys[i][0], keys[i][1]
    f.close()

#################################################################################
#   Find top data to energy ratio
#################################################################################


if args.top_hosts_data_to_energy_overall:
    top_energy = defaultdict(float)
    top_data = defaultdict(float)
    for hour in hours:

        for row in timeline.fetch_data(["app"], hour):
            (bandwidth_up, bandwidth_down, bandwidth_up_encrypted, \
                    bandwidth_down_encrypted, energy_wifi, \
                    energy_cellular, energy_per_byte_cellular, \
                    energy_per_byte_wifi, host) = row
            if float(bandwidth_up +  bandwidth_down) > 0:
                top_energy[host] += float(energy_wifi + energy_cellular)
                top_data[host] += float(bandwidth_up +  bandwidth_down)

    top_ratio = defaultdict(float)

    for k, v in top_energy.iteritems():
        if k in top_data and top_data[k] != 0:
            top_ratio[k] = v/top_data[k]

    keys = sorted(top_ratio.items(), key=operator.itemgetter(1), reverse=True)
    f = open("output_files/top_energy_ratio_hosts_overall.txt", "w")
    for i in range(len(keys)):
        if i < len(keys):
            print >>f, keys[i][0], keys[i][1]
    f.close()
#################################################################################
#  Make plot by user 
#################################################################################

if args.user_by_time:
    for hour in hours:
        for row in timeline.fetch_data(["userid"], hour):
            (bandwidth_up, bandwidth_down, bandwidth_up_encrypted, bandwidth_down_encrypted, user) = row
            print hour,bandwidth_up, bandwidth_down, bandwidth_up_encrypted, bandwidth_down_encrypted, user
        
#################################################################################
#  Make plot by content type 
#################################################################################

if args.content:

    f = open("output_files/top_total_hosts.txt")
    interesting_apps= []
    limit = 20
    for line in f:
        line = line.split()[0]
        interesting_apps.append(line)
        limit -= 1
        if limit == 0:
            break
    f.close()
    interesting_apps.append("all")

    interesting_content_type = ["image/jpg", "image/svg+xml", \
            "image/gif", "image/webp", "image/jpeg", "image/png", \
            "text/xml", "text/json", "text/html", "text/javascript"]

    app_files = {}
    for app in interesting_apps:
        app_filename = app.replace("/", "")
        app_files[app] = open("content_types/" + app_filename + ".txt", "w")

    
    # TODO: for each app, in a file, plot data size and energy evolution over time

    for hour in hours:

        content_data = {}
        for app in interesting_apps:
            content_data[app] = [[] for i in range(len(interesting_content_type))]
        
        for row in timeline.fetch_data_median(["content_type", "app"], hour):

            (bandwidth_up, bandwidth_down, bandwidth_up_encrypted, bandwidth_down_encrypted, energy_wifi, energy_cellular, energy_per_byte_wifi, energy_per_byte_cellular, content_type, app) = row

            if content_type not in interesting_content_type:
                continue

            content_index = interesting_content_type.index(content_type)
            
            if app not in interesting_apps:
                continue

            content_data[app][content_index] = [bandwidth_up, bandwidth_down, energy_cellular, energy_wifi, energy_per_byte_wifi, energy_per_byte_cellular]

#        for row in timeline.fetch_data_median(["content_type"], hour):
#
#            (bandwidth_up, bandwidth_down, bandwidth_up_encrypted, bandwidth_down_encrypted, energy_wifi, energy_cellular, energy_per_byte_wifi, energy_per_byte_cellular, content_type) = row
#            if content_type not in interesting_content_type:
#                continue
#            content_index = interesting_content_type.index(content_type)
#
#            content_data["all"][content_index] = [bandwidth_up, bandwidth_down, energy_cellular, energy_wifi, energy_per_byte_wifi, energy_per_byte_cellular]


        for appname, content in content_data.iteritems():
            printline = str(hour) + " "
            print_me = False
            f = app_files[appname]
            for item in content:
                if len(item) > 0:
                    item = [str(x) for x in item]
                    printline += " ".join(item) + " " 
                    print_me = True
                else:
                    printline += "0 0 0 0 0 0 "

            if print_me:
                print >> app_files[appname], printline

    for name, f in app_files.iteritems():
        f.close()

#################################################################################
#  Make plot 
#################################################################################

if args.user_by_host:
    f = open("output_files/top_upload_hosts.txt")
    upload_hosts = {} 
    key_order_up = []
    limit = 10
    for line in f:
        line = line.split()[0]
        upload_hosts[line] = 0
        key_order_up.append(line)
        limit -= 1
        if limit == 0:
            break
    upload_hosts["other"] = 0
    key_order_up.append("other")
    f.close()
        

    f = open("output_files/top_download_hosts.txt")
    key_order_down = []
    download_hosts = {} 
    limit = 10
    for line in f:
        line = line.split()[0]
        download_hosts[line] = 0
        key_order_down.append(line)
        limit -= 1
        if limit == 0:
            break
    key_order_down.append("other")
    download_hosts["other"] = 0
    f.close()

    f = open("output_files/by_user_host.txt", "w")

#    key_order_down = download_hosts.keys()

    print >>f,  " ".join(key_order_down),

#    key_order_up = upload_hosts.keys()

    print >>f, " ".join(key_order_up)
    
    for hour in hours:
        download_dict = {}
        upload_dict = {}
        download_dict_encrypted = {}
        upload_dict_encrypted = {}

#        download_dict = dict(download_hosts) 
#        upload_dict = dict(upload_hosts) 
#        download_dict_encrypted = dict(download_hosts) 
#        upload_dict_encrypted = dict(upload_hosts) 
        

        for row in timeline.fetch_data(["app", "userid"], hour):
            
            (bandwidth_up, bandwidth_down, bandwidth_up_encrypted, bandwidth_down_encrypted, host, user) = row

            if user not in download_dict:
                download_dict[user] = dict(download_hosts)
                upload_dict[user] = dict(upload_hosts) 
                download_dict_encrypted[user] = dict(download_hosts) 
                upload_dict_encrypted[user] = dict(upload_hosts) 

            if host in download_dict[user]:
                download_dict[user][host] += bandwidth_down
                download_dict_encrypted[user][host] += bandwidth_down_encrypted
            else:
                download_dict[user]["other"] += bandwidth_down
                download_dict_encrypted[user]["other"] += bandwidth_down_encrypted

            if host in upload_dict:
                upload_dict[user][host] += bandwidth_up
                upload_dict_encrypted[user][host] += bandwidth_up_encrypted
            else:
                upload_dict[user]["other"] += bandwidth_up
                upload_dict_encrypted[user]["other"] += bandwidth_up_encrypted

        for user in download_dict.keys():
            print >>f, hour, user, 
            for k in key_order_down:
                print >>f, download_dict[user][k],
                print >>f, download_dict_encrypted[user][k],
            for k in key_order_up:
                print >>f, upload_dict[user][k],
                print >>f, upload_dict_encrypted[user][k],
            print >>f

#timeline.generate_plot(["host"])


#353091053665792 2 170816854:43035|-1379776157:80 10.46.117.86:43035 173.194.73.99:80 -1.000000 1349330747.346620 1349330747.346620 1349330748.132947 1349330815.915398 1349330748.412880 884 804 1088 944 1.100260 0.279933 1349330839.675386 1012 868 442 402 0 0 8 application/json|*| AndroiddattIMMD|*|*|*|*|*|*|*| www.google.com|*|*|*|*|*|*|*| 96|96| 192

