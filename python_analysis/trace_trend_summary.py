#!/usr/bin/python

import c_session
import timeline
from collections import defaultdict
from IPy import IP
import socket
import operator

flows = c_session.CFlow()
flows.load_data()

timeline = timeline.TimeLine()

timestamp_adjustor = 3600 * 24

dns_lookup = {}

for item in flows.data:

    userid = item["userID"]
    is_encrypted =  (len(item["host"]) == 0)
    app = item["app_name"]

    size_up = item["total_dl_payload_h"]
    size_down = item["total_ul_payload_h"]
    content_type = item["content_type"]
    time = item["start_time"]
    
    size_up_encrypted = 0
    size_down_encrypted = 0

    if is_encrypted:
        size_up_encrypted = size_up 
        size_down_encrypted = size_down
        size_up = 0
        size_down = 0

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

    timeline.add_data_point(time, userid, app, -1, -1, content_type, size_up, size_down, size_up_encrypted, size_down_encrypted, timestamp_adjustor)
    # TODO encrypted or not encrypted

timeline.sync_to_database()

hours = timeline.fetch_all_hours()

#################################################################################
#   Get top hosts for downloads
#################################################################################

if True:
    top_downloads = defaultdict(int) 
    top_uploads = defaultdict(int) 
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


    f = open("top_upload_hosts.txt", "w")
    g = open("top_download_hosts.txt", "w")
    for i in range(100):
        if i < len(keys_up):
            print >>f, keys_up[i][0], keys_up[i][1]
        if i < len(keys_down):
            print >>g, keys_down[i][0], keys_down[i][1]
    f.close()
    g.close()

#################################################################################
#  Make plot 
#################################################################################

if False:
    f = open("top_upload_hosts.txt")
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
    f.close()

    f = open("top_download_hosts.txt")
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
    download_hosts["other"] = 0
    f.close()

#    key_order_down = download_hosts.keys()
    print " ".join(key_order_down),
#    key_order_up = upload_hosts.keys()
    print " ".join(key_order_up)
    
    for hour in hours:
        download_dict = dict(download_hosts) 
        upload_dict = dict(upload_hosts) 
        download_dict_encrypted = dict(download_hosts) 
        upload_dict_encrypted = dict(upload_hosts) 
        

        print hour,
        for row in timeline.fetch_data(["app"], hour):
            
            (bandwidth_up, bandwidth_down, bandwidth_up_encrypted, bandwidth_down_encrypted, host) = row
            if host in download_dict:
                download_dict[host] += bandwidth_down
                download_dict_encrypted[host] += bandwidth_down_encrypted
            else:
                download_dict["other"] += bandwidth_down
                download_dict_encrypted["other"] += bandwidth_down_encrypted

            if host in upload_dict:
                upload_dict[host] += bandwidth_up
                upload_dict_encrypted[host] += bandwidth_up_encrypted
            else:
                upload_dict["other"] += bandwidth_up
                upload_dict_encrypted["other"] += bandwidth_up_encrypted

        for k in key_order_down:
            print download_dict[k],
            print download_dict_encrypted[k],
        for k in key_order_up:
            print upload_dict[k],
            print upload_dict_encrypted[k],
        print

#timeline.generate_plot(["host"])


#353091053665792 2 170816854:43035|-1379776157:80 10.46.117.86:43035 173.194.73.99:80 -1.000000 1349330747.346620 1349330747.346620 1349330748.132947 1349330815.915398 1349330748.412880 884 804 1088 944 1.100260 0.279933 1349330839.675386 1012 868 442 402 0 0 8 application/json|*| AndroiddattIMMD|*|*|*|*|*|*|*| www.google.com|*|*|*|*|*|*|*| 96|96| 192

