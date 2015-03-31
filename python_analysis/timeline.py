#!/usr/bin/python

from collections import defaultdict

import MySQLdb
import config_private as config 
import string

##############################################################################
#
# This class is for taking data and turning it into a per-hour timeline of 
# statistics.
#
# It can be made to generate a printable output file that gnuplot, etc should
# be able to easily deal with.
#
# It is backed by an SQL database to help do the lookups etc more efficiently.
#
# TODO: treat entries where a field is left blank separately, so we can do
# some analysis in parallel without having full metadata about everything.
#
# TODO: add in battery consumption data
# 
##############################################################################

column_names = ["hour", "userid", "app", "location_rating", "network_type", \
        "content_type", "bandwidth_up", "bandwidth_down", "bandwidth_up_encrypted", "bandwidth_down_encrypted"]

def Tree():
    """ Is there a better way of making a tree?
    """ 
    return defaultdict(Tree)

class TimeLine:
    """ Data structure for managing entire data timeline.

    Mostly a wrapper for HourSummary."""

    def __init__(self, table_name="data_by_hour"): # make unique for each test
        self.timeline = {} 
        self.connection = MySQLdb.connect('localhost', config.mysql_username, \
                config.mysql_password, config.root_database)
        self.table_name = table_name

    def __del__(self):
        self.connection.close()


    def load_from_database(self, filename):
        """ If present, load from database"""

        query = "SELECT * FROM " + self.table_name
        cursor = self.connection.cursor()
        cursor.execute(query)
        for row in cursor.fetchall():
            self.add_data_point(*row)

    def sync_to_database(self):
        """ Save to database, clearing existing data """ 

        cursor = self.connection.cursor()
        cursor.execute("TRUNCATE TABLE " + self.table_name);
        for t, v in self.timeline.iteritems():
            v.save_to_database(t, cursor)
        self.connection.commit();

    def add_flow_item(self, item):
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

        self.add_data_point(time, userid, app, -1, -1, content_type, size_up, size_down, size_up_encrypted, size_down_encrypted, timestamp_adjustor)


    def add_data_point(self, timestamp, userid, app, location_rating, \
            network_type, content_type, bandwidth_up, bandwidth_down, bandwidth_up_encrypted, \
            bandwidth_down_encrypted, timestamp_adjustor = 1):
        """Figure out what timeline entry the data should be added to and add it there. """

        timestamp = timestamp / timestamp_adjustor 
        if timestamp not in self.timeline:
            self.timeline[timestamp] = HourSummary(timestamp, self.table_name)
        self.timeline[timestamp].add_data_point(userid, app, location_rating, \
                network_type, content_type, bandwidth_up, bandwidth_down, \
                bandwidth_up_encrypted, bandwidth_down_encrypted)

    def fetch_all_hours(self):
        """Returns a list of all unique times in order """
        cursor = self.connection.cursor()
        query = "SELECT DISTINCT hour FROM "+ self.table_name + " where HOUR >0 ORDER BY hour"
        hours = []
        cursor.execute(query)
        for hour in cursor.fetchall():
            hours.append(hour[0])
        return hours

    def fetch_match_column(self, filter_column, value, hour):
        """ Given an hour, a column and a value, sum up the bandwidths that match that."""

        query = "SELECT sum(bandwidth_up), sum(bandwidth_down) , sum(bandwidth_up_encrypted), sum(bandwdith_down_encrypted) FROM " + self.table_name + " WHERE hour=" + str(hour) + " AND " + filter_column + " = \"" + str(value) + "\""
        cursor = self.connection.cursor()
        cursor.execute(query)
        bandwidth_up = 0
        bandwidth_down = 0
        bandwidth_up_encrypted = 0
        bandwidth_down_encrypted = 0
        for row in cursor.fetchall():
            try:
                bandwidth_up += int(row[0])
                bandwidth_down += int(row[1])
                bandwidth_up_encrypted += int(row[2])
                bandwidth_down_encrypted += int(row[3])
            except:
                continue
        return (bandwidth_up, bandwidth_down, bandwidth_up_encrypted, bandwidth_down_encrypted)

        

    def fetch_data(self, filter_columns, hour):
        """Return results of query with unique summed values based on the 
        filters (table headings) given.
        
        """
        query = "SELECT sum(bandwidth_up), sum(bandwidth_down) , sum(bandwidth_up_encrypted), sum(bandwidth_down_encrypted) "

        group_by = "hour"
        if filter_columns:
            query += "," + ", ".join(filter_columns)
            group_by += "," + ", ".join(filter_columns)
        query += (" FROM "+ self.table_name + " where hour = " + str(hour) + "  GROUP BY " + group_by)
        cursor = self.connection.cursor()
        cursor.execute(query)
        for row in cursor.fetchall():
            yield row

    def generate_plot(self, filter_columns):
        """ Generate a plottable list of data based on the filters (table headings) given. 
        Time and bandwidth are selected by default.

        Must have already loaded all data into the database.
        """

        query = "SELECT hour, sum(bandwidth_up), sum(bandwidth_down) , sum(bandwidth_up_encrypted), sum(bandwidth_down_encrypted)"

        group_by = "hour"
        if filter_columns:
            query += "," + ", ".join(filter_columns)
            group_by += "," + ", ".join(filter_columns)
        query += " FROM " + self.table_name + " GROUP BY " + group_by
        cursor = self.connection.cursor()
#        print query
        cursor.execute(query)
        for row in cursor.fetchall():
            to_print = [str(x) for x in row]
            print " ".join(to_print)

class HourSummary:
    """ Breakdown of bandwidth in each time slot summarized by various data types.
    
    Structure as a tree in rough order of how likely we are to query just that."""

    def __init__(self, time, table_name):
        self.time = time
        self.total_bandwidth = 0

        self.location_tree = Tree() 
        self.table_name = table_name

    def save_to_database(self, time, cursor):
        for user, v in self.location_tree.iteritems():
            for app, v2 in v.iteritems():
                for location_rating, v3 in v2.iteritems():
                    for content_type, v4 in v3.iteritems():
                        for network_type, bandwidth in v4.iteritems():
                            values = [time, user, app, location_rating, \
                                    network_type, content_type, \
                                    bandwidth[0], bandwidth[1], bandwidth[2], bandwidth[3]]
                            values = self.__clean_values(values)
                            query = "INSERT INTO "+ self.table_name + " (" + \
                                    ", ".join(column_names) + ") Values (" + \
                                    ", ".join(values) + ")" 
#                            print query
                            try:
                                cursor.execute(query)
                            except:
                                print query

    def __clean_values(self, l):
        """ Prepare list for loading into a database"""
        ret_l = []
        for item in l:
            if isinstance(item, str):
                item = filter(lambda x: x in string.printable, item)
                item = item.replace("\'", "")
                item = item.replace("\"", "")

                item = "\"" + item + "\""
            else:
                item = str(item)
            if len(item) == 0:
               item = "NULL"
            ret_l.append(item)
        return ret_l


    def add_data_point(self, userid, app, location_rating, network_type, \
            content_type, bandwidth_up, bandwidth_down,  bandwidth_up_encrypted, bandwidth_down_encrypted):
        """ Each parameter is another 'level' of the tree, bandwidth is additive."""

        # We need to convert the leaves to ints rather than dicts 
        if (network_type) not in self.location_tree[userid][app][location_rating][content_type]:
            self.location_tree[userid][app][location_rating][content_type][network_type] = [0, 0, 0, 0]

        self.location_tree[userid][app][location_rating][content_type][network_type][1] += bandwidth_down
        self.location_tree[userid][app][location_rating][content_type][network_type][0] += bandwidth_up
        self.location_tree[userid][app][location_rating][content_type][network_type][3] += bandwidth_down_encrypted
        self.location_tree[userid][app][location_rating][content_type][network_type][2] += bandwidth_up_encrypted

if __name__ == "__main__":
    """ For testing only at this point"""
    
    timeline = TimeLine()
    timeline.add_data_point(1, 2, 3, 4, 5, 6, 7, 7)
    timeline.add_data_point(1, 2, 3, 4, 5, 7, 8, 5)
    timeline.add_data_point(2, 3, 4, 5, 6, 7, 9, 4)
    timeline.add_data_point(3, 4, 5, 6, 7, 8, 10, 3)
    timeline.add_data_point(2, 2, 3, 4, 5, 6, 11, 2)
    
    timeline.sync_to_database()
    timeline.generate_plot(["location_rating", "network_type"])

