#!/usr/bin/python

from collections import defaultdict

import MySQLdb
import config_private 

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

column_names = ["hour", "userid", "app", "location_rating", "network_type", "bandwidth"]

def Tree():
   """ Is there a better way of making a tree?""" 
    return defaultdict(Tree)


class TimeLine:
    """ Data structure for managing entire data timeline.

    Mostly a wrapper for HourSummary."""
    def __init__(self):
        self.timeline = defaultdict(HourSummary)


    def load_from_database(self, filename):
        """ If present, load from database"""
        connection = MySQLdb.connect('localhost', config.mysql_username, config.mysql_password, config.root_database)

        query = "SELECT * FROM data_by_hour"
        cursor = connection.cursor()
        cursor.execute(query)
        for row in cursor.fetchall():
            self.add_data_point(*row)

    def sync_to_database(self):
        """ Save to database, clearing existing data """ 
        connection = MySQLdb.connect('localhost', config.mysql_username, config.mysql_password, config.root_database)
        cursor = self.connection.cursor()
        cursor.execute("TRUNCATE TABLE data_by_hour");
        for t, v in self.timeline.iteritems():
            v.save_to_database(t, cursor)
        connection.commit();
        connection.close();


    def add_data_point(self, timestamp, userid, app, location_rating, network_type, bandwidth, timestamp_adjustor = 1):
        """Figure out what timeline entry the data should be added to and add it there. """
        timestamp = timestamp / 3600 
        timeline[timestamp].add_data_point(userid, app, location_rating, network_type, banwidth)

    def generate_plot(self, filter_columns):
        """ Generate a plottable list of data based on the filters (table headings) given. 
        Time and bandwidth are selected by default.

        Must have already loaded all data into the database.
        """
        connection = MySQLdb.connect('localhost', config.mysql_username, config.mysql_password, config.root_database)
        query = "SELECT hour, sum(bandwidth) "

        group_by = "hour"
        if filter_columns:
            query += "," + ", ".join(filter_columns)
            group_by += "," + ", ".join(filter_columns)
        query += " FROM data_by_hour GROUP BY" + group_by
        cursor =  
        

class HourSummary:

    """ Breakdown of bandwidth in each time slot summarized by various data types.
    
    Structure as a tree in rough order of how likely we are to query just that."""
    def __init__(self, time):
        self.time = time
        self.total_bandwidth = 0

        self.location_tree = Tree() 

    def save_to_database(self, time, cursor):
        for user, v in self.location_tree.iteritems():
            for app, v2 in self.v.iteritems():
                for location_rating, v3 in self.v2.iteritems():
                    for network_type, bandwidth in self.v3.iteritems():
                        values = [time, user, app, location_rating, network_type, bandwidth]
                        cursor.execute("INSERT INTO data_by_hour (" + ", ".join(column_names) + ") Values (" + ", ".join(values)) 

    def add_data_point(self, userid, app, location_rating, network_type, bandwidth):
        """ Each parameter is another 'level' of the tree, bandwidth is additive."""

        # We need to convert the leaves to ints rather than dicts 
        if (network_type) not in self.location_tree[userid][app][location_rating]:
            self.location_tree[userid][app][location_rating] = defaultdict(int)

        self.location_tree[userid][app][location_rating][network_type] += bandwidth







if __name__ == "__main__":
    """ For testing only at this point"""
    
    timeline = TimeLine()
    timeline.add_data_point(1, 2, 3, 4, 5, 6)
    timeline.add_data_point(1, 2, 3, 4, 5, 7)
    timeline.add_data_point(2, 3, 4, 5, 6, 7)
    timeline.add_data_point(3, 4, 5, 6, 7, 8)
    timeline.add_data_point(2, 2, 3, 4, 5, 6)
    
    timeline.sync_to_database()
    timeline.generate_plot("location_rating", "network_type")




