#!/usr/bin/python

import c_session
from collections import defaultdict
import operator
import sys
import numpy
from  IPy import IP

browser_list = ["com.android.chrome", "com.android.browser", "org.mozilla.firefox", "mobi.mgeek.TunnyBrowser"]

def print_distribution(l, suffix=""):
    print suffix, max(l), numpy.median(l), min(l), numpy.mean(l), numpy.std(l)

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
        self.urls_energy = defaultdict(int)

        self.flow_length = defaultdict(list)
        self.flow_size = defaultdict(list)

        self.analyze_url = {}

        self.analyze_content_type = {}

        self.up_all = 0
        self.down_all = 0
        self.count_all = 0
        self.energy_all = 0

        self.match_metric = {}
        self.sizes = []
        self.energies = []
#        self.download = download

    def add_host(self, host, up, down, flow_length, energy):

        self.urls[host] += 1
        self.urls_up[host] += up
        self.urls_down[host] += down
        self.urls_energy[host] += energy

        self.count_all += 1
        self.up_all += up
        self.down_all += down
        self.energy_all += energy

        self.sizes.append(up)
        self.energies.append(energy)

        self.match_metric[host] = url_package_match_heuristic(host, self.appname)
        self.flow_length[host].append(flow_length)
        self.flow_size[host].append(up)

    def add_sub_url(self, host, up, down, energy, url, flow_length):

        full_host = host
        host_root = host.split(".")
        if len(host_root) >= 2:
            host = ".".join(host_root[-2:]) 

        if host not in self.analyze_url:
            self.analyze_url[host] = SubUrl(host)
        self.analyze_url[host].add_url(url, up, energy, flow_length)
        self.analyze_url[host].add_extra_host(full_host)

    def add_content_type(self, content_type, up, down, energy):
        content_type = content_type.split("/")
        if len(content_type) != 2:
            category = content_type[0]
            subcategory = "none"
        else:
            (category, subcategory) = content_type
        if category not in self.analyze_content_type:
            self.analyze_content_type[category] = {}
        if subcategory not in self.analyze_content_type[category]:
            self.analyze_content_type[category][subcategory] = ContentType()
        self.analyze_content_type[category][subcategory].add_content_type(up+ down, energy)

    def printme(self):

        print "========================================="
        print self.appname
        print "========================================="

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
        sort_by_energy = sorted(self.urls_energy.items(), key=operator.itemgetter(1), reverse=True)

        print "Top by count:",
        for i in range(min(10, len(sort_by_count))):
            print "\t", sort_by_count[i][0], print_ratio(sort_by_count[i][1], self.count_all)
        print

        print "Top by data:",
        for i in range(min(10, len(sort_by_data))):
            print "\t", sort_by_data[i][0], print_ratio(sort_by_data[i][1], self.up_all)
        print

        print "Top by length:",
        for i in range(min(10, len(sort_by_length))):
            print "\t", sort_by_length[i][0], sort_by_length[i][1] 
        print

        print "Top by energy:",
        for i in range(min(10, len(sort_by_energy))):
            print "\t", sort_by_energy[i][0], print_ratio(sort_by_energy[i][1], self.energy_all)
        print

        print "URL CDF:"
        for i in range(len(sort_by_count)-1,-1, -1):
            print len(sort_by_count)-i, sort_by_count[i][1], sort_by_data[i][1], sort_by_length[i][1], sort_by_energy[i][1]
        print

        print "URL SCATTERPLOT:"
        for k in self.urls.keys():
            print self.urls[k], self.urls_up[k], flow_length[k], self.urls_energy[k]

        print "Number of urls", len(sort_by_count)
        print "Longest flow", max_overall
        print "Average size overall", numpy.mean(self.sizes)
        print "Energy overall", self.energy_all 
        print "Average size of highest reqests", numpy.mean(self.flow_size[sort_by_count[i][0]])
        print "Average size of largest reqests", numpy.mean(self.flow_size[sort_by_data[i][0]])
        print "Average size of longest reqests", numpy.mean(self.flow_size[sort_by_length[i][0]])
        print "Energy per request", numpy.mean(self.energies)
        print "Sizes", self.up_all

        vals = sorted(self.urls.items(), key=operator.itemgetter(1), reverse=True)
        for item in vals:
            k = item[0]
            v = item[1]

            print "\t", k, print_ratio(v, self.count_all), print_ratio(self.urls_up[k], self.up_all), print_ratio(self.urls_down[k], self.down_all), self.match_metric[k]
            print_distribution(self.flow_length[k], "\t\t")  
            
            self.analyze_url[k].printme()

        self.print_content()

    def print_content(self):
        for k, v in self.analyze_content_type.iteritems():
            print "****************", k, "*******************"
            for k2, v2 in v.iteritems():
                v2.printline(k2)

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
    
    def add_sub_url(self, host, up, down, energy, url, app, flow_length):
        full_host = host
        host_root = host.split(".")

        if len(host_root) >= 2:
            host = ".".join(host_root[-2:]) 

        if app not in self.analyze_url:
            self.analyze_url[app] = SubUrl(host)

        self.analyze_url[app].add_url(url, up, energy, flow_length)
        self.analyze_url[app].add_extra_host(full_host)

    def printme(self, hostname):

        if len(self.package_count_by_app) <= 1:
            return
        print "================================"
        print hostname

        vals = sorted(self.package_count_by_app.items(), key=operator.itemgetter(1), reverse=True)

        for item in vals:
            (k, v) = item
            print "\t", k, print_ratio(v, self.total_count_by_app),\
                    print_ratio(self.package_down_by_app[k], self.total_down_by_app),\
                    print_ratio(self.package_up_by_app[k], self.total_up_by_app)
            self.analyze_url[item[0]].printme()

class ContentType:
    def __init__(self):
        self.sizes = []
        self.energy = []


    def add_content_type(self, size, energy):
        self.sizes.append(size)
        self.energy.append(energy)

    def printline(self, k2):
        sizes = numpy.mean(self.sizes)
        sizes_variation = numpy.std(self.sizes)
        energy = numpy.mean(self.energy)
        energy_variation = numpy.std(self.energy)
        print "\t", k2, sizes, sizes_variation, len(self.sizes), energy, energy_variation, len(self.energy)


class SubUrl:
    def __init__(self, host):

        self.host = host 

        self.parameters = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))

        self.urls = defaultdict(int)
        self.url_energy = defaultdict(int)
        self.url_data = defaultdict(int)

        self.extra_host = defaultdict(int)

        self.total_urls = 0
        self.filter_uniques = True
        self.flow_lengths = []

    def add_url(self, url, data, energy, flow_length):
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
        self.url_energy[url] += energy
        self.url_data[url] += data 
        self.flow_lengths.append(flow_length)

    def add_extra_host(self, host):
        host = host.split(".")
        if len(host) > 2:
            host = ".".join(host[:-2])
            self.extra_host[host] += 1

    def printme(self):
#        print "\t---------------------"
#        print "\t", self.host

#        vals = sorted(self.urls.items(), key=operator.itemgetter(1), reverse=True)
#        for item in vals:
#            print "\t", item[0], item[1]
#            if item[0] in self.parameters:
#                for k, v in self.parameters[url].iteritems():
#                    print k, " ".join(v.keys())

        self.collapse_url_tree()

#                parameter_vals = sorted(self.parameters[item[0], key=operator.itemgetter(1), reverse=True]
#                for 

        print "\t\t", "----"
        if len(self.extra_host) > 1:
            vals = sorted(self.extra_host.items(), key=operator.itemgetter(1), reverse=True)
            for item in vals:
                if float(item[1])/self.total_urls > 0.05:
                    print "\t\t", item[0], item[1]

        print_distribution(self.flow_lengths, "\t\t\t")  
#        for k, v in self.parameters.iteritems():
#            vals = sorted(v.items(), key=operator.itemgetter(1), reverse=True)
#            for item in vals:
#                print item[0], item[1]

            
        # time distribution
        # parameters 

    def collapse_url_tree(self):

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
                    last_tree[item]["POWER"] = 0
                    last_tree[item]["DATA"] = 0
                last_tree[item]["VALUE"] += 1
                last_tree[item]["POWER"] += self.url_energy[root_url]
                last_tree[item]["DATA"] += self.url_data[root_url]

                last_tree = last_tree[item]
        (name, root) = self.__collapse_url_tree(root, None)
        self.__print_tree(root, 0)
        
        # collapse the tree

    def __collapse_url_tree(self, tree, name):
        keys = tree.keys()

        if "VALUE" in keys:
            value = tree["VALUE"]
            keys.remove("VALUE")
        else:
            value = 0

        if "POWER" in keys:
            power = tree["POWER"]
            keys.remove("POWER")
        else:
            power = 0

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
            d["POWER"] = power 
            return (subname, d)
        elif len(keys) == 0:
            return (name, Tree())
        else:
            new_dict = Tree()
            for k, v in tree.iteritems():
                if k == "VALUE" or k == "DATA" or k== "POWER":
                    continue
                if name == None:
                    new_full_name = k
                else:
                    new_full_name = name + "/" + k 
                (subname, d) = self.__collapse_url_tree(v, new_full_name)
                new_dict[subname] = d
            new_dict["VALUE"] = value
            new_dict["DATA"] = data 
            new_dict["POWER"] = power
            return (name, new_dict)


    def __print_tree(self, tree, n):
        for k, v in tree.iteritems():
            if isinstance(v, int) or isinstance(v, float):
                continue
            print "\t\t",
            for i in range(n):
                print "\t",
            if k != None:
                value = -1
                data = -1
                power= -1
                if "VALUE" in v and v["VALUE"] != 0:
                    value = v["VALUE"]
                if "DATA" in v and v["DATA"] != 0:
                    data = v["DATA"]
                if "POWER" in v and v["POWER"] != 0:
                    power = v["POWER"]
                print k, value, data, power, 1024*power/data, power/value
            self.__print_tree(v, n+1)

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
    app = item["app_name"]
    size_up = item["total_dl_whole"]
    size_down = item["total_ul_whole"]
    content_type = item["content_type"]
    time = item["start_time"]
    urls = item["request_url"]
    hosts = item["host"]
    network_type = item["network_type"]

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
        appname_analysis[app].add_host(host, size_up, size_down, energy, flow_length)
        match_heuristic =url_package_match_heuristic(host, app) 
        if match_heuristic > 1:
#            print host, app, match_heuristic 
            lines_heuristic += 1

        if host not in host_analysis:
            host_analysis[host] = AnalyzeHostTrends()
        host_analysis[host].add_app(app, size_up, size_down, flow_length)

        appname_analysis[app].add_sub_url(full_host, size_up, size_down, energy, url, flow_length)
        host_analysis[host].add_sub_url(full_host, size_up, size_down, energy, url, app, flow_length)

        appname_analysis[app].add_content_type(mimetype, size_up, size_down, energy)
        all_analysis.add_content_type(mimetype, size_up, size_down, energy)

print "================================================"
print "START"

all_analysis.print_content()

for k, v in appname_analysis.iteritems():
    v.printme()

print "================================================="
print "HOST SOURCE ANALYSIS"
print "================================================="

for k, v in host_analysis.iteritems():
    v.printme(k)

#print "================================================="
#print "URL BREAKDOWN"
#print "================================================="

#for host, sub_url in sub_url_analysis.iteritems():
#    sub_url.printme()

total = float(lines_loaded)
print "Fraction processed:", lines_processed/total, "", lines_heuristic/total, \
        "Total loaded:", lines_loaded 

print url_package_match_heuristic("android.clients.google.com", "com.google.android.gm")

