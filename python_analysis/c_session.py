#!/usr/bin/python

# NOT ACTUALLY TESTED YET!

class CLogs:
    """Superclass for loading and parsing C logs """
    def __init__(self, filename, data_format_labels, data_format_types):

        self.data = []
        self.filename = "/z/user-study-imc15/PACO/" + filename
        self.data_format_labels = data_format_labels
        self.data_format_types = data_format_types
#        self.load_data()


    def load_data(self, limit=-1):

        f =open(self.filename)
        for line in f:
            if limit != -1:
                limit -= 1
            line = line.strip()
            line = line.split(" ")

            # Some lines are mangled...
            # This should happen rarely though
            if len(line) != len(self.data_format_labels) or len(line) != len(self.data_format_types):
                print "Warning: line length wrong, expected", len(self.data_format_labels), len(self.data_format_types), len(line)
                print "\t", line
                continue

            # convert data to the appropriate type e.g. ["a", "1", "2"] + [str, int, int] 
            # becomes ["a", 1, 2]
            line = [datatype(val) for (datatype, val) in zip(self.data_format_types, line)]

            new_item= dict(zip(self.data_format_labels, line)) 
            self.data.append(new_item)
            if limit == 0:
                break

        f.close()

    def clean_c_string(self, line):
        if "|" not in line:
            return line
        retval = []
        line = line.split("|")
        last_item = None
        for item in line:
            if item == "*":
                if last_item != None:
                    retval.append(last_item)
            else:
                last_item = item
                retval.append(item)
        return retval

class CSession(CLogs):

    """ Load + interact with user session data.
    
    Equivalent to filetype 4 from the C files. 
    Summary of all data from one user.  
    """

    def __init__(self):
        data_format_labels = ["user_id",\
                    "start_time",\
                    "end_time",\
                    "ul_ip_all",\
                    "ul_ip_payload",\
                    "ul_tcp_all",\
                    "ul_tcp_payload",\
                    "ul_udp_all",\
                    "ul_udp_payload",\
                    "dl_ip_all",\
                    "dl_ip_payload",\
                    "dl_tcp_all",\
                    "dl_tcp_payload",\
                    "dl_udp_all",\
                    "dl_udp_payload"]
        data_format_types = [str, float, float, int, int, int, int, int, int, \
                int, int, int, int, int,int]
        CLogs.__init__(self, "session_summary.txt", data_format_labels, data_format_types)


class CRate(CLogs):
    """  One flow. """
    def __init__(self):
        separator = " "
        data_format_labels = ["is_down",\
            "userID", \
            "start_time", \
            "start_time_binned ", \
            "end_time", \
            "ip_all", \
            "ip_payload", \
            "tcp_all", \
            "tcp_payload", \
            "udp_all", \
            "udp_payload"]

        # convert ul to boolean
        data_format_types = [ lambda x: x == "dl", \
            str, float, float, float, int, int, int, int, int]
 
        CLogs.__init__(self, "rate_summary.txt", data_format_labels, data_format_types)




class CFlow(CLogs):
    """ TODO finish
    
    TCP flow specifically"""
    def __init__(self):
   
        parse_port_tuple = lambda x: x.split(":")

#        clean_c_str = lambda x: x.replace("|", "").replace("*", "")
 
        data_format_labels = ["userID", \
            "tcp_flows_size", \
            # what is this?
            "unique_flow_id",\
            # these include ports
            "clt_ip_tuple",\
            "server_ip_tuple",\
            "packet_count",\
            "app_packet_count",\
            "app_name",\
            "start_time", \
            "tmp_start_time",\
            "first_ul_pl_time", \
            "first_dl_pl_time",\
            "last_ul_pl_time", \
            "last_dl_pl_time",\
            "total_ul_payload", \
            "total_dl_payload",\
            "total_ul_whole", \
            "total_dl_whole",\
            "ul_time", \
            "dl_time", \
            "last_tcp_ts",\
            "total_ul_payload_h", \
            "total_dl_payload_h",\
            "ul_rate_payload", \
            "dl_rate_payload",\
            "ul_rate_payload_h", \
            "dl_rate_payload_h",\
            "http_request_count",\
            "content_type", \
            "user_agent",\
            "host",\
            "content_length",\
            "total_content_length",\
            "request_url"]

        
        data_format_types = [str, \
                int,\
                str,\
                parse_port_tuple,\
                parse_port_tuple,\
                int,\
                int,\
                str,\
                float, \
                float,\
                float,\
                float,\
                float,\
                float,\
                int,\
                int,\
                int,\
                int,\
                float,\
                float,\
                float,\
                int,\
                int,\
                int,\
                int,\
                int,\
                int,\
                int,\
                self.clean_c_string,\
                self.clean_c_string,\
                self.clean_c_string,\
                self.clean_c_string,\
                int,\
                self.clean_c_string,]

        CLogs.__init__(self,"flow_summary.txt", data_format_labels, data_format_types)
            
if __name__ == "__main__":
    """ For testing only at this point"""
    flows = CFlow()
    flows.load_data(100)
    for item in flows.data:

        print item 
