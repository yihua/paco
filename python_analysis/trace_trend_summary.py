#!/usr/bin/python

import c_session
import timeline
from collections import defaultdict
from IPy import IP
import socket

flows = c_session.CFlow()
flows.load_data()

timeline = timeline.TimeLine()

timestamp_adjustor = 3600 * 24

dns_lookup = {}

for item in flows.data:
    userid = item["userID"]
    app =  item["host"]
    size_up = item["total_dl_payload_h"]
    size_down = item["total_ul_payload_h"]
    content_type = item["content_type"]
    time = item["start_time"]

    app = app.split(":")[0]
    try:
        # will throw an exception if not an IP
        IP(app)
        if app not in dns_lookup:
            host = socket.gethostbyaddr(app)
            dns_lookup[app] = host
    except:
        pass

    app = app.split(".")
    if len(app) >= 2:
        app = ".".join(app[-2:])
    else:
        continue
    timeline.add_data_point(time, userid, app, -1, -1, content_type, size_up, size_down, timestamp_adjustor)
    # TODO encrypted or not encrypted

timeline.sync_to_database()

hours = timeline.fetch_all_hours()

#################################################################################
#   Get top hosts for downloads
#################################################################################


if False:
    top_downloads = defaultdict(int) 
    top_uploads = defaultdict(int) 
    for hour in hours:
        host_ratings_up = defaultdict(int) 
        host_ratings_down = defaultdict(int)
        for row in timeline.fetch_data(["app"], hour):

            (bandwidth_up, bandwidth_down, host) = row
            host_ratings_up[host] += bandwidth_up
            host_ratings_down[host] += bandwidth_down

        keys_up = host_ratings_up.keys()
        keys_up.sort()
        for i in range(min(5, len(keys_up))):
            top_uploads[keys_up[i]] += host_ratings_up[keys_up[i]]

        keys_down = host_ratings_down.keys()
        keys_down.sort()
        for i in range(min(5, len(keys_down))):
            top_downloads[keys_down[i]] += host_ratings_down[keys_down[i]]

    keys_up = top_uploads.keys()
    keys_up.sort()
    keys_down = top_downloads.keys()
    keys_down.sort()
    f = open("top_upload_hosts.txt", "w")
    g = open("top_download_hosts.txt", "w")
    for i in range(100):
        if i < len(keys_up):
            print >>f, keys_up[i]
        if i < len(keys_down):
            print >>g, keys_down[i]
    f.close()
    g.close()

#################################################################################
#  Make plot 
#################################################################################

if True:
    f = open("top_upload_hosts.txt")
    upload_hosts = {} 
    limit = 10
    for line in f:
        upload_hosts[line.strip()] = 0
        limit -= 1
        if limit == 0:
            break
    f.close()

    f = open("top_download_hosts.txt")
    download_hosts = []
    limit = 10
    for line in f:
        download_hosts[line.strip()] = 0
        limit -= 1
        if limit == 0:
            break
    f.close()
    
    for hour in hours:
        download_dict = dict(download_hosts) 

        print hour,
        for row in timeline.fetch_data(["app"], hour):
            for key in download_dict.keys():
                print timeline.fetch_match_column("app", key, hour),
        
        upload_dict = dict(upload_hosts) 
        for row in timeline.fetch_data(["app"], hour):
            for key in upload_dict.keys():
                print timeline.fetch_match_column("app", key, hour),

    

#timeline.generate_plot(["host"])


#353091053665792 2 170816854:43035|-1379776157:80 10.46.117.86:43035 173.194.73.99:80 -1.000000 1349330747.346620 1349330747.346620 1349330748.132947 1349330815.915398 1349330748.412880 884 804 1088 944 1.100260 0.279933 1349330839.675386 1012 868 442 402 0 0 8 application/json|*| AndroiddattIMMD|*|*|*|*|*|*|*| www.google.com|*|*|*|*|*|*|*| 96|96| 192

