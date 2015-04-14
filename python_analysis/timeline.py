#!/usr/bin/python

from collections import defaultdict

import numpy
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


def Tree():
    """ Is there a better way of making a tree?
    """ 
    return defaultdict(Tree)

class TimeLine:
    """ Data structure for managing entire data timeline.

    Mostly a wrapper for HourSummary."""

    def __init__(self, table_name="data_by_hour", column_names = None): # make unique for each test
        self.timeline = {} 
        self.connection = MySQLdb.connect('localhost', config.mysql_username, \
                config.mysql_password, config.root_database)
        self.table_name = table_name

        if column_names != None:
            self.column_names = column_names
        else:
            self.column_names = ["hour", "userid", "app", "location_rating", "network_type", \
                    "content_type", "bandwidth_up", "bandwidth_down", "bandwidth_up_encrypted", "bandwidth_down_encrypted", "energy_wifi", "energy_cellular", "energy_per_byte_wifi", "energy_per_byte_cellular"]

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

    def __add_flow_item_helper(self, start_time, userid, app, energy, \
            content_type, size_up, size_down, is_encrypted, is_wifi, \
            timestamp_adjustor):

        size_up_encrypted = 0
        size_down_encrypted = 0

        energy_wifi = 0
        energy_cellular = 0

        energy_per_byte_wifi = -1
        energy_per_byte_cellular = -1

        if energy > 0 and size_up + size_down <= 0:
            print "ERROR!!!", start_time, userid, app, energy, content_type, size_up, size_down, is_encrypted, is_wifi
            exit()
        
        if is_wifi:
            energy_wifi = energy 
            if size_up + size_down > 0:
                energy_per_byte_wifi = energy_wifi / (size_up + size_down) 
        else:
            energy_cellular = energy 
            if size_up + size_down > 0:
                energy_per_byte_cellular = energy_cellular / (size_up + size_down)

        if is_encrypted:
            size_down_encrypted = size_down
            size_up_encrypted = size_up
            size_up = 0
            size_down = 0

        self.add_data_point(start_time, userid, app, -1, -1, content_type, \
                size_up, size_down, size_up_encrypted, size_down_encrypted, \
                energy_wifi, energy_cellular, energy_per_byte_wifi, \
                energy_per_byte_cellular, timestamp_adjustor)

    def add_flow_item(self, item, timestamp_adjustor):
        userid = item["userID"]
        is_encrypted =  (len(item["host"]) == 0)
        app = item["app_name"].split(":")[0]

        is_wifi = (item["network_type"] == 0)

        content_types = item["content_type"]
        sizes = item["content_length"]
        energies = item["energy_log"]
        timestamps = item["timestamp_log"]
      
        if len(sizes) == 0:
            if item["first_ul_pl_time"] > 0 and item["first_dl_pl_time"] > 0:
                start_time = min(item["first_ul_pl_time"], item["first_dl_pl_time"])
            elif item["first_ul_pl_time"] > 0:
                start_time = item["first_ul_pl_time"]
            else:
                start_time = item["first_dl_pl_time"]

            energy = item["active_energy"] + item["passive_energy"]
            content_type = "none"
            size_up = item["total_ul_whole"]
            size_down = item["total_dl_whole"] 

            self.__add_flow_item_helper(start_time, userid, app, energy,\
                    content_type, size_up, size_down, is_encrypted, \
                    is_wifi, timestamp_adjustor)

        for i in range(len(sizes)):
            try:
                energy_down, energy_up = energies[i].split(",")
                energy = float(energy_down) + float(energy_up)
                content_type = content_types[i]
                size_up = int(sizes[i]) + item["total_ul_payload_h"]/len(sizes) + item["total_dl_payload_h"]/len(sizes)
                if size_up == 0:
                    size_up = (item["total_ul_whole"] +  item["total_dl_whole"])/len(sizes)

                size_down = 0
                timestamp = float(timestamps[i].split(",")[0])
            except:
                break

            self.__add_flow_item_helper(timestamp, userid, app, energy, \
                    content_type, size_up, size_down, is_encrypted, is_wifi,\
                    timestamp_adjustor)  

    def add_data_point(self, timestamp, row1, row2, row3, \
            row4, row5, bandwidth_up, bandwidth_down, bandwidth_up_encrypted, \
            bandwidth_down_encrypted, energy_wifi, energy_cellular, \
            energy_per_byte_wifi, energy_per_byte_cellular, timestamp_adjustor = 1):
        """Figure out what timeline entry the data should be added to and add it there. """

#        print bandwidth_up, bandwidth_down
        timestamp = timestamp / timestamp_adjustor 
        if timestamp not in self.timeline:
            self.timeline[timestamp] = HourSummary(timestamp, self.table_name, self.column_names)
        self.timeline[timestamp].add_hour_point(row1, row2, row3, \
                row4, row5, bandwidth_up, bandwidth_down, \
                bandwidth_up_encrypted, bandwidth_down_encrypted, \
                energy_wifi, energy_cellular, energy_per_byte_wifi, \
                energy_per_byte_cellular)

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

        query = "SELECT sum(bandwidth_up), sum(bandwidth_down) , sum(bandwidth_up_encrypted), sum(bandwdith_down_encrypted), sum(energy_wifi), sum(energy_cellular), avg(nullif(energy_per_byte_cellular,-1)), avg(nullif(energy_per_byte_wifi, -1)) FROM " + self.table_name + " WHERE hour=" + str(hour) + " AND " + filter_column + " = \"" + str(value) + "\""
        cursor = self.connection.cursor()
        cursor.execute(query)
        bandwidth_up = 0
        bandwidth_down = 0
        bandwidth_up_encrypted = 0
        bandwidth_down_encrypted = 0
        energy_wifi = 0
        energy_cellular = 0
        energy_per_byte_wifi = []
        energy_per_byte_cellular = []
        for row in cursor.fetchall():
            try:
                bandwidth_up += int(row[0])
                bandwidth_down += int(row[1])
                bandwidth_up_encrypted += int(row[2])
                bandwidth_down_encrypted += int(row[3])
                energy_wifi += float(row[4])
                energy_cellular += float(row[5])

                energy_per_byte_wifi.append(float(row[6]))
                energy_per_byte_cellular.append(float(row[7]))
            except:
                continue

        if len(energy_per_byte_wifi) > 0:
            energy_per_byte_wifi = sum(energy_per_byte_wifi)/len(energy_per_byte_wifi)
        else:
            energy_per_byte_wifi = -1

        if len(energy_per_byte_cellular) > 0:
            energy_per_byte_cellular = sum(energy_per_byte_cellular)/len(energy_per_byte_cellular)
        else:
            energy_per_byte_cellular = -1

        return (bandwidth_up, bandwidth_down, bandwidth_up_encrypted, bandwidth_down_encrypted, energy_wifi, energy_cellular, energy_per_byte_wifi, energy_per_byte_cellular)
    
    def fetch_data_median(self, filter_columns, hour):
        query = "SELECT bandwidth_up, bandwidth_down, bandwidth_up_encrypted, bandwidth_down_encrypted, energy_wifi, energy_cellular, energy_per_byte_wifi, energy_per_byte_cellular "

        group_by = "hour"
        if filter_columns:
            query += "," + ", ".join(filter_columns)
            group_by += "," + ", ".join(filter_columns)
        query += (" FROM "+ self.table_name + " where hour = " + str(hour) + "  GROUP BY " + group_by)


        cursor = self.connection.cursor()
        cursor.execute(query)

        bandwidth_up = []
        bandwidth_down = []
        bandwidth_up_encrypted = []
        bandwidth_down_encrypted = []
        energy_wifi = []
        energy_cellular = []
        energy_per_byte_wifi = []
        energy_per_byte_cellular = []

        last_app = None
        last_content_type = None
        for row in cursor.fetchall():
            if row[8] != last_app and row[9] != last_content_type and \
                    last_app != None and last_content_type != None:

                yield numpy.mean(bandwidth_up), numpy.mean(bandwidth_down), \
                        numpy.mean(bandwidth_up_encrypted), \
                        numpy.mean(bandwidth_down_encrypted), \
                        numpy.mean(energy_wifi), numpy.mean(energy_cellular), \
                        numpy.mean(energy_per_byte_wifi), \
                        numpy.mean(energy_per_byte_cellular), \
                        last_app, last_content_type

                bandwidth_up = []
                bandwidth_down = []
                bandwidth_up_encrypted = []
                bandwidth_down_encrypted = []
                energy_wifi = []
                energy_cellular = []
                energy_per_byte_wifi = []
                energy_per_byte_cellular = []

            bandwidth_up.append(row[0])
            bandwidth_down.append(row[1])
            bandwidth_up_encrypted.append(row[2])
            bandwidth_down_encrypted.append(row[3])
            energy_wifi.append(row[4])
            energy_cellular.append(row[5])
            energy_per_byte_wifi.append(row[6])
            energy_per_byte_cellular.append(row[7])

            last_app = row[8]
            last_content_type = row[9]

        for row in cursor.fetchall():
            yield row

    def fetch_data_averages(self, filter_columns, hour):
        query = "SELECT avg(nullif(bandwidth_up, -1)), avg(nullif(bandwidth_down, -1)) , avg(nullif(bandwidth_up_encrypted, -1)), avg(nullif(bandwidth_down_encrypted, -1)), avg(nullif(energy_wifi, -1)), avg(nullif(energy_cellular, -1)), avg(nullif(energy_per_byte_wifi,-1)), avg(nullif(energy_per_byte_cellular, -1)) "

        group_by = "hour"
        if filter_columns:
            query += "," + ", ".join(filter_columns)
            group_by += "," + ", ".join(filter_columns)
        query += (" FROM "+ self.table_name + " where hour = " + str(hour) + "  GROUP BY " + group_by)
        cursor = self.connection.cursor()
        cursor.execute(query)
        for row in cursor.fetchall():
            yield row

    def fetch_data(self, filter_columns, hour):
        """Return results of query with unique summed values based on the 
        filters (table headings) given.
        
        """
        query = "SELECT sum(bandwidth_up), sum(bandwidth_down) , sum(bandwidth_up_encrypted), sum(bandwidth_down_encrypted), sum(energy_wifi), sum(energy_cellular), avg(nullif(energy_per_byte_wifi,-1)), avg(nullif(energy_per_byte_cellular, -1)) "

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

        query = "SELECT hour, sum(bandwidth_up), sum(bandwidth_down) , sum(bandwidth_up_encrypted), sum(bandwidth_down_encrypted), sum(energy_wifi), sum(energy_cellular)"

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
    
    Structure as a tree in rough order of how likely we are to query just that.
    
    TODO tree structure now completely useless, refactor"""

    def __init__(self, time, table_name, column_names):
        self.time = time
        self.total_bandwidth = 0

        self.location_tree = Tree() 
        self.table_name = table_name
        self.column_names = column_names

    def save_to_database(self, time, cursor):
        for row1, v in self.location_tree.iteritems():
            for row2, v2 in v.iteritems():
                for row3, v3 in v2.iteritems():
                    for row4, v4 in v3.iteritems():
                        for row5, data in v4.iteritems():
                            energy_per_byte_wifi = data[6]

                            if len(energy_per_byte_wifi) > 0:
                                energy_per_byte_wifi = sum(energy_per_byte_wifi)/\
                                        len(energy_per_byte_wifi)
                            else:
                                energy_per_byte_wifi = 0
                            
                            energy_per_byte_cellular = data[7]

                            if len(energy_per_byte_cellular) > 0:
                                energy_per_byte_cellular = sum(energy_per_byte_cellular)/\
                                        len(energy_per_byte_cellular)
                            else:
                                energy_per_byte_cellular = 0

                            values = [time, row1, row2, row3, row4, row5,\
                                    data[0], data[1], data[2], data[3], data[4], data[5], energy_per_byte_wifi, energy_per_byte_cellular]
                            values = self.__clean_values(values)
                            query = "INSERT INTO "+ self.table_name + " (" + \
                                    ", ".join(self.column_names) + ") Values (" + \
                                    ", ".join(values) + ")" 
#                            print query
                            try:
                                cursor.execute(query)
                            except:
                                print "ERROR!"
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


    def add_hour_point(self, row1, row2, row3, row4, row5, bandwidth_up, bandwidth_down,  bandwidth_up_encrypted, bandwidth_down_encrypted, energy_wifi, energy_cellular, energy_per_byte_wifi, energy_per_byte_cellular):
        """ Each parameter is another 'level' of the tree, bandwidth is additive."""

        # We need to convert the leaves to ints rather than dicts 
        if (row5) not in self.location_tree[row1][row2][row3][row4]:
            self.location_tree[row1][row2][row3][row4][row5] = [0, 0, 0, 0, 0, 0, [], []]

        self.location_tree[row1][row2][row3][row4][row5][1] += bandwidth_down
        self.location_tree[row1][row2][row3][row4][row5][0] += bandwidth_up
        self.location_tree[row1][row2][row3][row4][row5][3] += bandwidth_down_encrypted
        self.location_tree[row1][row2][row3][row4][row5][2] += bandwidth_up_encrypted
        self.location_tree[row1][row2][row3][row4][row5][4] += energy_wifi 
        self.location_tree[row1][row2][row3][row4][row5][5] += energy_cellular 
        self.location_tree[row1][row2][row3][row4][row5][6].append(energy_per_byte_wifi)  
        self.location_tree[row1][row2][row3][row4][row5][7].append(energy_per_byte_cellular)  

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

