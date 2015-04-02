#!/usr/bin/python

import c_session
from collections import defaultdict
import operator
import sys

browser_list = ["com.android.chrome", "com.android.browser", "org.mozilla.firefox", "mobi.mgeek.TunnyBrowser"]

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
        self.flow_length = defaultdict(list)

        self.analyze_url = {}

        self.up_all = 0
        self.down_all = 0
        self.count_all = 0


        self.match_metric = {}
#        self.download = download

    def add_host(self, host, up, down, flow_length):

        self.urls[host] += 1
        self.urls_up[host] += up
        self.urls_down[host] += down

        self.count_all += 1
        self.up_all += up
        self.down_all += down

        self.match_metric[host] = url_package_match_heuristic(host, self.appname)
        self.flow_length[host].append(flow_length)

    def add_sub_url(self, host, up, down, url, flow_length):
        full_host = host
        host_root = host.split(".")
        if len(host_root) >= 2:
            host = ".".join(host_root[-2:]) 

        if host not in self.analyze_url:
            self.analyze_url[host] = SubUrl(host)
        self.analyze_url[host].add_url(url, flow_length)
        self.analyze_url[host].add_extra_host(full_host)

    def printme(self):
        print "========================================="
        print self.appname
        print "========================================="
        vals = sorted(self.urls.items(), key=operator.itemgetter(1), reverse=True)
        for item in vals:
            k = item[0]
            v = item[1]
            avg_flow_length = sum(self.flow_length[k])/len(self.flow_length[k])

            print "\t", k, print_ratio(v, self.count_all), print_ratio(self.urls_up[k], self.up_all), print_ratio(self.urls_down[k], self.down_all), self.match_metric[k], avg_flow_length
            self.analyze_url[k].printme()

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
    
    def add_sub_url(self, host, up, down, url, app, flow_length):
        full_host = host
        host_root = host.split(".")

        if len(host_root) >= 2:
            host = ".".join(host_root[-2:]) 

        if app not in self.analyze_url:
            self.analyze_url[app] = SubUrl(host)

        self.analyze_url[app].add_url(url, flow_length)
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

class SubUrl:
    def __init__(self, host):

        self.host = host 

        self.parameters = defaultdict(lambda:defaultdict(lambda:defaultdict(int)))
        self.urls = defaultdict(int)
        self.extra_host = defaultdict(int)
        self.total_urls = 0
        self.filter_uniques = True
        self.flow_lengths = []

    def add_url(self, url, flow_length):
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
            if float(count)/self.total_urls < 0.05:# and False:
                continue
            url = url.strip("/")

            url = url.split("/")

            last_tree = root

            for item in url:
                if item not in last_tree:
                    last_tree[item]["VALUE"] = 0
                last_tree[item]["VALUE"] += 1
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

        if len(keys) == 1 and name != None:
            old_subname = keys[0]
            full_name = name + "/" +old_subname
            (subname, d) = self.__collapse_url_tree(tree[old_subname], full_name)
            d["VALUE"] = value
            return (subname, d)
        elif len(keys) == 0:
            return (name, Tree())
        else:
            new_dict = Tree()
            for k, v in tree.iteritems():
                if k == "VALUE":
                    continue
                if name == None:
                    new_full_name = k
                else:
                    new_full_name = name + "/" + k 
                (subname, d) = self.__collapse_url_tree(v, new_full_name)
                new_dict[subname] = d
            new_dict["VALUE"] = value
            return (name, new_dict)


    def __print_tree(self, tree, n):
        for k, v in tree.iteritems():
            if isinstance(v, int):
                continue
            print "\t\t",
            for i in range(n):
                print "\t",
            if k != None:
                if "VALUE" in v:
                    print v["VALUE"],
                print k
            self.__print_tree(v, n+1)

upload_hosts = []
download_hosts = []

f = open("output_files/top_upload_hosts.txt")
limit = 10
for line in f:
    line = line.split()[0]
    upload_hosts.append(line)
    limit -= 1
    if limit == 0:
        break
f.close()

f = open("output_files/top_download_hosts.txt")
limit = 10
for line in f:
    line = line.split()[0]
    download_hosts.append(line)
    limit -= 1
    if limit == 0:
        break
f.close()

flows = c_session.CFlow()

flows.load_data(limit=500000)

lines_loaded = 0
lines_processed = 0
lines_heuristic = 0

appname_analysis = {}
sub_url_analysis = {}

host_analysis = {}

for item in flows.data:
    userid = item["userID"]
    is_encrypted = (len(item["host"]) == 0)
    lines_loaded += 1

    if is_encrypted:
        continue
    lines_processed += 1
    app = item["app_name"]
    size_up = item["total_dl_payload_h"]
    size_down = item["total_ul_payload_h"]
    content_type = item["content_type"]
    time = item["start_time"]
    urls = item["request_url"]
    hosts = item["host"]

    flow_length = max(item["last_ul_pl_time"], item["last_dl_pl_time"]) - \
            min(item["first_ul_pl_time"], item["first_dl_pl_time"]) 

    if len(urls) > 0:
        urls = urls[1:]

    if app not in upload_hosts:
        continue

    if app in browser_list or app == "none":
        continue
    
    if len(urls) != len(hosts):
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

        full_host = host
        host_root = host.split(".")
        if len(host_root) >= 2:
            host = ".".join(host_root[-2:]) 

        if app not in appname_analysis:
            appname_analysis[app] = AnalyzeAppUrls(app)
        appname_analysis[app].add_host(host, size_up, size_down, flow_length)
        match_heuristic =url_package_match_heuristic(host, app) 
        if match_heuristic > 1:
#            print host, app, match_heuristic 
            lines_heuristic += 1

        if host not in host_analysis:
            host_analysis[host] = AnalyzeHostTrends()
        host_analysis[host].add_app(app, size_up, size_down, flow_length)


        appname_analysis[app].add_sub_url(full_host, size_up, size_down, url, flow_length)
        host_analysis[host].add_sub_url(full_host, size_up, size_down, url, app, flow_length)


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

