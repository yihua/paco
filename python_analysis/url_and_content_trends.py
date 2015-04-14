#!/usr/bin/python

import c_session
from collections import defaultdict
import operator
import sys
import numpy
from  IPy import IP

#browser_list = ["com.android.chrome", "com.android.browser", "org.mozilla.firefox", "mobi.mgeek.TunnyBrowser"]
browser_list = []

def print_distribution(l, f, suffix=""):
    print >>f, suffix, max(l), numpy.median(l), min(l), numpy.mean(l), numpy.std(l)

def print_ratio(nominator, denumerator):
    ratio = 100*float(nominator)/denumerator
    
    return "{0:.2f}".format(ratio)

def Tree():
        return defaultdict(Tree)

def url_package_match_heuristic(url, package):

    metric = 0
    if "com.android" in package:
        if "google.com" in url or \
                "googleusercontent.com" in url or \
                "ggpht.com" in url:
            metric += 1

    if "com.facebook" in package:
        if "fbcdn.com" in package:
            metric += 1

    url = url.split(".")
    package = package.split(".")
    for (i, segment) in enumerate(package):
        if i < len(url):
            if segment == url[-(i+1)]:
                metric += 1
            elif segment in url[-i]:
                metric += 0.5
    return metric

class AnalyzeAppUrls:

    def __init__(self, appname):

        self.appname = appname
        self.urls = defaultdict(int)
        self.urls_up = defaultdict(int)
        self.urls_down = defaultdict(int)
        self.urls_energy_cellular = defaultdict(int)
        self.urls_energy_wifi = defaultdict(int)

        self.flow_length = defaultdict(list)
        self.flow_size = defaultdict(list)

        self.analyze_url = {}

        self.analyze_content_type = {}

        self.up_all = 0
        self.down_all = 0
        self.count_all = 0
        self.energy_cellular_all = 0
        self.energy_wifi_all = 0

        self.match_metric = {}
        self.sizes = []
        self.energies_cellular = []
        self.energies_wifi = []
#        self.download = download

#    def add_host(self, host, up, down, flow_length, energy, is_wifi):

#        self.urls[host] += 1
#        self.download = download

    def add_host(self, host, up, down, flow_length, energy, is_wifi):

        self.urls[host] += 1
        self.urls_up[host] += up
        self.urls_down[host] += down
        if is_wifi:
            self.urls_energy_wifi[host] += energy
            self.energies_wifi.append(energy)
        else:
            self.urls_energy_cellular[host] += energy
            self.energies_cellular.append(energy)

        self.count_all += 1
        self.up_all += up
        self.down_all += down
        self.energy_cellular_all += energy
        self.energy_wifi_all += energy

        self.sizes.append(up)

        self.match_metric[host] = url_package_match_heuristic(host, self.appname)
        self.flow_length[host].append(flow_length)
        self.flow_size[host].append(up)

    def add_sub_url(self, host, up, down, energy, url, flow_length, is_wifi):

        full_host = host
        host_root = host.split(".")
        if len(host_root) >= 2:
            host = ".".join(host_root[-2:]) 

        if host not in self.analyze_url:
            self.analyze_url[host] = SubUrl(host)
        self.analyze_url[host].add_url(url, up, energy, flow_length, is_wifi)
        self.analyze_url[host].add_extra_host(full_host)

    def add_content_type(self, content_type, up, down, energy, is_wifi):

        content_type = content_type.split("/")
        if len(content_type) != 2:
            category = content_type[0]
            subcategory = "none"
        else:
            (category, subcategory) = content_type

        if subcategory == "jpg":
            subcategory = "jpeg"

        if category not in self.analyze_content_type:
            self.analyze_content_type[category] = {}
        if subcategory not in self.analyze_content_type[category]:
            self.analyze_content_type[category][subcategory] = ContentType()
        self.analyze_content_type[category][subcategory].add_content_type(up+ down, energy, is_wifi)

    def printme(self, f):

        print  >>f, "========================================="
        print  >>f, self.appname
        print  >>f, "========================================="

        flow_length = defaultdict(int)
        max_overall = 0
        for k, v in self.flow_length.iteritems():
            flow_length[k] = numpy.mean(v)
            max_here = max(v)
            if max_here > max_overall:
                max_overall = max_here

        sort_by_count = sorted(self.urls.items(), key=operator.itemgetter(1), reverse=True)
        sort_by_data = sorted(self.urls_up.items(), key=operator.itemgetter(1), reverse=True)
        sort_by_length = sorted(flow_length.items(), key=operator.itemgetter(1), reverse=True)
        sort_by_energy_cellular = sorted(self.urls_energy_cellular.items(), key=operator.itemgetter(1), reverse=True)
        sort_by_energy_wifi = sorted(self.urls_energy_wifi.items(), key=operator.itemgetter(1), reverse=True)

        print >>f,  "Top by count:",
        for i in range(min(10, len(sort_by_count))):
            print  >>f, "\t", sort_by_count[i][0], print_ratio(sort_by_count[i][1], self.count_all)
        print >>f

        print  >>f, "Top by data:",
        for i in range(min(10, len(sort_by_data))):
            print  >>f, "\t", sort_by_data[i][0], print_ratio(sort_by_data[i][1], self.up_all)
        print >>f

        print  >>f, "Top by length:",
        for i in range(min(10, len(sort_by_length))):
            print  >>f, "\t", sort_by_length[i][0], sort_by_length[i][1] 
        print >>f

        print  >>f, "Top by cellular energy:",
        for i in range(min(10, len(sort_by_energy_cellular))):
            print >>f, "\t", sort_by_energy_cellular[i][0], print_ratio(sort_by_energy_cellular[i][1], self.energy_cellular_all)
        print >>f

        print  >>f, "Top by wifi energy:",
        for i in range(min(10, len(sort_by_energy_wifi))):
            print >>f, "\t", sort_by_energy_wifi[i][0], print_ratio(sort_by_energy_wifi[i][1], self.energy_wifi_all)
        print >>f

        print >>f, "URL CDF:"
        for i in range(len(sort_by_count)-1,-1, -1):
            print >>f, len(sort_by_count)-i, sort_by_count[i][1], sort_by_data[i][1], \
                    sort_by_length[i][1]
        print >>f

        print >>f, "URL CDF, wifi:"
        for i in range(len(sort_by_energy_wifi)-1,-1, -1):
            print >>f,  len(sort_by_energy_wifi)-i, sort_by_energy_wifi[i][1]
        print >>f

        print >>f, "URL CDF, cellular:"
        for i in range(len(sort_by_energy_cellular)-1,-1, -1):
            print >>f,  len(sort_by_energy_cellular)-i, sort_by_energy_cellular[i][1]
        print >>f

        print  >>f, "URL SCATTERPLOT:"
        for k in self.urls.keys():
            print >>f, self.urls[k], self.urls_up[k], flow_length[k]#, self.urls_energy[k]

        print >>f,  "Number of urls", len(sort_by_count)
        print >>f,  "Longest flow", max_overall
        print >>f,  "Average size overall", numpy.mean(self.sizes)
        print >>f,  "Energy overall (wifi) ", self.energy_wifi_all
        print >>f,  "Energy overall (cellular) ", self.energy_cellular_all
        print >>f,  "Average size of highest reqests", numpy.mean(self.flow_size[sort_by_count[i][0]])
        print >>f,  "Average size of largest reqests", numpy.mean(self.flow_size[sort_by_data[i][0]])
        print >>f,  "Average size of longest reqests", numpy.mean(self.flow_size[sort_by_length[i][0]])
        print >>f,  "Energy per request (cellular)", numpy.mean(self.energies_cellular)
        print >>f,  "Energy per request (wifi)", numpy.mean(self.energies_wifi)
        print >>f,  "Sizes", self.up_all

        vals = sorted(self.urls.items(), key=operator.itemgetter(1), reverse=True)
        for item in vals:
            k = item[0]
            v = item[1]

            print >>f,  "\t", k, print_ratio(v, self.count_all), print_ratio(self.urls_up[k], self.up_all), print_ratio(self.urls_down[k], self.down_all), self.match_metric[k]
            print_distribution(self.flow_length[k], f, "\t\t")  
            
            self.analyze_url[k].printme(f)

        self.print_content(f)

    def print_content(self, f):
        for k, v in self.analyze_content_type.iteritems():
            print >>f, "****************", k, "*******************"
            for k2, v2 in v.iteritems():
                v2.printline(k2, f)

class AnalyzeHostTrends:

    def __init__(self):

        self.package_count_by_app = defaultdict(int)
        self.package_up_by_app = defaultdict(int)
        self.package_down_by_app = defaultdict(int)

        self.flow_lengths = defaultdict(list)

        self.total_count_by_app = 0
        self.total_up_by_app = 0
        self.total_down_by_app = 0
        self.analyze_url = {}

    def add_app(self, app, size_up, size_down, flow_length):

        self.package_count_by_app[app] += 1
        self.package_up_by_app[app] += size_up
        self.package_down_by_app[app] += size_down
        self.flow_lengths[app].append(flow_length)

        self.total_count_by_app += 1
        self.total_up_by_app += size_up
        self.total_down_by_app += size_down
    
    def add_sub_url(self, host, up, down, energy, url, app, flow_length, is_wifi):
        full_host = host
        host_root = host.split(".")

        if len(host_root) >= 2:
            host = ".".join(host_root[-2:]) 

        if app not in self.analyze_url:
            self.analyze_url[app] = SubUrl(host)

        self.analyze_url[app].add_url(url, up, energy, flow_length, is_wifi)
        self.analyze_url[app].add_extra_host(full_host)

    def printme(self, hostname, f):

        if len(self.package_count_by_app) <= 1:
            return
        print >>f, "================================"
        print >>f, hostname

        vals = sorted(self.package_count_by_app.items(), key=operator.itemgetter(1), reverse=True)

        for item in vals:
            (k, v) = item
            print >>f, "\t", k, print_ratio(v, self.total_count_by_app),\
                    print_ratio(self.package_down_by_app[k], self.total_down_by_app),\
                    print_ratio(self.package_up_by_app[k], self.total_up_by_app)
            self.analyze_url[item[0]].printme(f)

class ContentType:
    def __init__(self):
        self.sizes = []
        self.energy_cellular = []
        self.energy_wifi = []
        self.energy_cellular_ratio = []
        self.energy_wifi_ratio = []


    def add_content_type(self, size, energy, is_wifi):
        self.sizes.append(size)
        if is_wifi:
            self.energy_wifi.append(energy)
            if size > 0:
                self.energy_wifi_ratio.append(energy/size)
        else:
            self.energy_cellular.append(energy)
            if size > 0:
                self.energy_cellular_ratio.append(energy/size)

    def printline(self, k2, f):
        if len(self.sizes) > 0:
            sizes = numpy.median(self.sizes)
            sizes_max = numpy.percentile(self.sizes, 95)
            sizes_min = numpy.percentile(self.sizes, 5)
        else:
            return

        if len(self.energy_cellular) > 0:
            energy_cellular = numpy.median(self.energy_cellular)
            energy_cellular_max = numpy.percentile(self.energy_cellular, 95)
            energy_cellular_min = numpy.percentile(self.energy_cellular, 5)
        else:
            energy_cellular = -1
            energy_cellular_max = -1
            energy_cellular_min = -1

        if len(self.energy_wifi) > 0:
            energy_wifi = numpy.median(self.energy_wifi)
            energy_wifi_max = numpy.percentile(self.energy_wifi, 95)
            energy_wifi_min = numpy.percentile(self.energy_wifi, 5)
        else:
            energy_wifi = -1
            energy_wifi_max = -1
            energy_wifi_min = -1
    
        if len(self.energy_wifi_ratio) > 0:
            energy_wifi_ratio = numpy.median(self.energy_wifi_ratio)
            energy_wifi_ratio_max = numpy.percentile(self.energy_wifi_ratio, 95)
            energy_wifi_ratio_min = numpy.percentile(self.energy_wifi_ratio, 5)
        else:
            energy_wifi_ratio = -1
            energy_wifi_ratio_max = -1
            energy_wifi_ratio_min = -1

        if len(self.energy_cellular_ratio) > 0:
            energy_cellular_ratio = numpy.median(self.energy_cellular_ratio)
            energy_cellular_ratio_max = numpy.percentile(self.energy_cellular_ratio, 95)
            energy_cellular_ratio_min = numpy.percentile(self.energy_cellular_ratio, 5)
        else:
            energy_cellular_ratio = -1
            energy_cellular_ratio_max = -1
            energy_cellular_ratio_min = -1

        print >>f, "\t", k2, sizes, sizes_max, sizes_min, len(self.sizes), \
                energy_cellular, energy_cellular_max, energy_cellular_min, \
                len(self.energy_cellular), energy_wifi, energy_wifi_max, \
                energy_wifi_min, len(self.energy_wifi),energy_wifi_ratio, \
                energy_wifi_ratio_max, energy_wifi_ratio_min, \
                len(self.energy_wifi_ratio), energy_cellular_ratio, \
                energy_cellular_ratio_max, energy_cellular_ratio_min, \
                len(self.energy_cellular_ratio)

class SubUrl:
    def __init__(self, host):

        self.host = host 

        self.parameters = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))

        self.urls = defaultdict(int)
        self.url_energy_cellular = defaultdict(int)
        self.url_energy_wifi = defaultdict(int)
        self.url_data = defaultdict(int)

        self.extra_host = defaultdict(int)

        self.total_urls = 0
        self.filter_uniques = True
        self.flow_lengths = []

    def add_url(self, url, data, energy, flow_length, is_wifi):
        if "?" in url:
            (url, parameters) = url.split("?", 1)
            if "&" in parameters:
                parameters = parameters.split("&")
                for param_segment in parameters:
                    if "=" not in param_segment:
                        continue
                    (key, val) = param_segment.split("=",1)
                    self.parameters[url][key][val] += 1

        self.total_urls += 1
        self.urls[url] += 1

        if is_wifi:
            self.url_energy_wifi[url] += energy
        else:
            self.url_energy_cellular[url] += energy

        self.url_data[url] += data 
        self.flow_lengths.append(flow_length)

    def add_extra_host(self, host):
        host = host.split(".")
        if len(host) > 2:
            host = ".".join(host[:-2])
            self.extra_host[host] += 1

    def printme(self, f):
#        print "\t---------------------"
#        print "\t", self.host

#        vals = sorted(self.urls.items(), key=operator.itemgetter(1), reverse=True)
#        for item in vals:
#            print "\t", item[0], item[1]
#            if item[0] in self.parameters:
#                for k, v in self.parameters[url].iteritems():
#                    print k, " ".join(v.keys())

        self.collapse_url_tree(f)

#                parameter_vals = sorted(self.parameters[item[0], key=operator.itemgetter(1), reverse=True]
#                for 

        print >>f, "\t\t", "----"
        if len(self.extra_host) > 1:
            vals = sorted(self.extra_host.items(), key=operator.itemgetter(1), reverse=True)
            for item in vals:
                if float(item[1])/self.total_urls > 0.05:
                    print >>f, "\t\t", item[0], item[1]

        print_distribution(self.flow_lengths, f, "\t\t\t")  
#        for k, v in self.parameters.iteritems():
#            vals = sorted(v.items(), key=operator.itemgetter(1), reverse=True)
#            for item in vals:
#                print item[0], item[1]

            
        # time distribution
        # parameters 

    def collapse_url_tree(self, f):

        # Make the tree
        root = Tree()
        for url, count in self.urls.iteritems():
            root_url = url
            if float(count)/self.total_urls < 0.05:# and False:
                continue
            url = url.strip("/")

            url = url.split("/")

            last_tree = root

            for item in url:
                if item not in last_tree:
                    last_tree[item]["VALUE"] = 0
                    last_tree[item]["POWER_WIFI"] = 0
                    last_tree[item]["POWER_CELL"] = 0
                    last_tree[item]["DATA"] = 0
                last_tree[item]["VALUE"] += 1
                last_tree[item]["POWER_CELL"] += self.url_energy_cellular[root_url]
                last_tree[item]["POWER_WIFI"] += self.url_energy_wifi[root_url]
                last_tree[item]["DATA"] += self.url_data[root_url]

                last_tree = last_tree[item]
        (name, root) = self.__collapse_url_tree(root, None)
        self.__print_tree(root, 0, f)
        
        # collapse the tree

    def __collapse_url_tree(self, tree, name):
        keys = tree.keys()

        if "VALUE" in keys:
            value = tree["VALUE"]
            keys.remove("VALUE")
        else:
            value = 0

        if "POWER_CELL" in keys:
            power_cell = tree["POWER_CELL"]
            keys.remove("POWER_CELL")
        else:
            power_cell = 0

        if "POWER_WIFI" in keys:
            power_wifi = tree["POWER_WIFI"]
            keys.remove("POWER_WIFI")
        else:
            power_wifi = 0


        if "DATA" in keys:
            data = tree["DATA"]
            keys.remove("DATA")
        else:
            data = 0

        if len(keys) == 1 and name != None:
            old_subname = keys[0]
            full_name = name + "/" +old_subname
            (subname, d) = self.__collapse_url_tree(tree[old_subname], full_name)
            d["VALUE"] = value
            d["DATA"] = data 
            d["POWER_CELL"] = power_cell 
            d["POWER_WIFI"] = power_wifi 
            return (subname, d)
        elif len(keys) == 0:
            return (name, Tree())
        else:
            new_dict = Tree()
            for k, v in tree.iteritems():
                if k == "VALUE" or k == "DATA" or k== "POWER_CELL" or k == "POWER_WIFI":
                    continue
                if name == None:
                    new_full_name = k
                else:
                    new_full_name = name + "/" + k 
                (subname, d) = self.__collapse_url_tree(v, new_full_name)
                new_dict[subname] = d
            new_dict["VALUE"] = value
            new_dict["DATA"] = data 
            new_dict["POWER_CELL"] = power_cell
            new_dict["POWER_WIFI"] = power_wifi
            return (name, new_dict)


    def __print_tree(self, tree, n, f):
        for k, v in tree.iteritems():
            if isinstance(v, int) or isinstance(v, float):
                continue
            print >>f, "\t\t",
            for i in range(n):
                print >>f, "\t",
            if k != None:
                value = -1
                data = -1
                power_cell = -1
                power_wifi = -1
                if "VALUE" in v and v["VALUE"] != 0:
                    value = v["VALUE"]
                if "DATA" in v and v["DATA"] != 0:
                    data = v["DATA"]
                if "POWER_CELL" in v and v["POWER_CELL"] != 0:
                    power_cell = v["POWER_CELL"]
                if "POWER_WIFI" in v and v["POWER_WIFI"] != 0:
                    power_cell = v["POWER_WIFI"]
                print >>f, k, value, data, power_cell, 1024*power_cell/data, power_cell/value, \
                        power_wifi, 1024*power_wifi/data, power_wifi/value
            self.__print_tree(v, n+1, f)

test_hosts = []

f = open("output_files/top_total_hosts.txt")
limit = 25 
for line in f:
    line = line.split()[0]
    test_hosts.append(line)
    limit -= 1
    if limit == 0:
        break
f.close()

#test_hosts = set()
#test_hosts.update(download_hosts)
#test_hosts.update(upload_hosts)

flows = c_session.CFlow()

flows.load_data()
#flows.load_data(limit=500000)

lines_loaded = 0
lines_processed = 0
lines_heuristic = 0

appname_analysis = {}
sub_url_analysis = {}

host_analysis = {}

all_analysis = AnalyzeAppUrls("all")

for item in flows.data:
    userid = item["userID"]
    is_encrypted = (len(item["host"]) == 0)
    lines_loaded += 1

    if is_encrypted:
        continue
    lines_processed += 1
    app = item["app_name"].split(":")[0]
    size_up = item["total_dl_whole"]
    size_down = item["total_ul_whole"]
    content_type = item["content_type"]
    time = item["start_time"]
    urls = item["request_url"]
    hosts = item["host"]
    is_wifi = (item["network_type"] == 0)

    energy_list = item["energy_log"]
    
    if item["first_ul_pl_time"] > 0 and item["first_dl_pl_time"] > 0:
        start_time = min(item["first_ul_pl_time"], item["first_dl_pl_time"])
    elif item["first_ul_pl_time"] > 0:
        start_time = item["first_ul_pl_time"]
    else:
        start_time = item["first_dl_pl_time"]

    if item["last_ul_pl_time"] > 0 and item["last_dl_pl_time"] > 0:
        end_time = max(item["last_ul_pl_time"], item["last_dl_pl_time"])
    elif item["last_ul_pl_time"] > 0:
        end_time = item["last_ul_pl_time"]
    else:
        end_time = item["last_dl_pl_time"]

    flow_length = end_time - start_time

    if len(urls) > 0:
        urls = urls[1:]

    if app not in test_hosts:
        continue

    if app in browser_list or app == "none":
        continue
    
    if len(urls) != len(hosts) or len(urls) != len(energy_list) or len(urls) != len(content_type):
        if "fonts.googleapis.com" in hosts and len(urls) == 3:
            urls = [urls[0] + "|" + urls[1], ""]
        else:
            if False:
                print >> sys.stderr, "MISMATCH!"
                for url in urls:
                    print >> sys.stderr, ":", url
                print>> sys.stderr
                for host in hosts:
                    print >> sys.stderr, ":", host
            continue

    for (i, host) in enumerate(hosts):
        if len(host) == 0:
            continue
   
        url = urls[i]
        energy_down, energy_up = energy_list[i].split(",")
        energy = float(energy_down) + float(energy_up)

        mimetype = content_type[i]

        full_host = host
        host_root = host.split(".")

        if len(host_root) >= 2:
            if len(host_root) == 4:
                try:
                    IP(full_host)
                except:
                    host = ".".join(host_root[-2:]) 
            host = ".".join(host_root[-2:]) 

        if app not in appname_analysis:
            appname_analysis[app] = AnalyzeAppUrls(app)
        appname_analysis[app].add_host(host, size_up, size_down, energy, flow_length, is_wifi)
        match_heuristic =url_package_match_heuristic(host, app) 
        if match_heuristic > 1:
#            print host, app, match_heuristic 
            lines_heuristic += 1

        if host not in host_analysis:
            host_analysis[host] = AnalyzeHostTrends()
        host_analysis[host].add_app(app, size_up, size_down, flow_length)

        appname_analysis[app].add_sub_url(full_host, size_up, size_down, energy, url, flow_length, is_wifi)
        host_analysis[host].add_sub_url(full_host, size_up, size_down, energy, url, app, flow_length, is_wifi)

        appname_analysis[app].add_content_type(mimetype, size_up, size_down, energy, is_wifi)
        all_analysis.add_content_type(mimetype, size_up, size_down, energy, is_wifi)
f = open("output_files/url_content_trends.txt", "w")
#print >>f, "================================================"
#print >>f, "START"

all_analysis.print_content(f)

for k, v in appname_analysis.iteritems():
    v.printme(f)

print >>f,  "================================================="
print >>f,  "HOST SOURCE ANALYSIS"
print >>f,  "================================================="

for k, v in host_analysis.iteritems():
    v.printme(k, f)

#print "================================================="
#print "URL BREAKDOWN"
#print "================================================="

#for host, sub_url in sub_url_analysis.iteritems():
#    sub_url.printme()

total = float(lines_loaded)
print "Fraction processed:", lines_processed/total, "", lines_heuristic/total, \
        "Total loaded:", lines_loaded 

#print url_package_match_heuristic("android.clients.google.com", "com.google.android.gm")

