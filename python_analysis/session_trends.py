#!/usr/bin/python

import timestream


class SessionAttribute(timestream.AttributeItem):
    
    def __init__(self, user, begin_time, end_time, session_id):

        self.energy_tail = 0
        self.energy_active = 0

        self.byte_upload = 0
        self.byte_download = 0

        self.byte_encrypted = 0

        # Not mutually exclusive
        self.had_wifi = False
        self.had_cellular = False

        self.active_apps = set()

        other_data = {"session_id": session_id, "session_length": end_time - begin_time}
        timestream.AttributeItem.__init__(self, user, begin_time, end_time, other_data)

    def merge_timeline_item(self, timeline_item):
        self.energy_tail += timeline_item.data["passive_energy"]
        self.energy_active += timeline_item.data["active_energy"]

        if timeline_item.data["is_wifi"]:
            self.had_wifi = True
        else:
            self.had_cellular = True

        self.byte_upload += timeline_item.data["flow_ul_payload"]
        self.byte_download += timeline_item.data["flow_dl_payload"]

        if timeline_item.data["flow_encrypted"]:
            self.byte_encrypted += (timeline_item.data["flow_ul_payload"] + \
                    timeline_item.data["flow_dl_payload"])
        self.active_apps.add(timeline_item.data["app_name"])

    def print_summary(self):
        if self.had_wifi:
            self.had_wifi = 1
        else:
            self.had_wifi = 0

        if self.had_cellular:
            self.had_cellular = 1
        else:
            self.had_cellular = 0

        f = open("output_files/session_summary.txt", "w")
        print >>f, self.other_data["session_id"], \
                self.other_data["session_length"], \
                self.energy_tail, self.energy_active, \
                self.had_wifi, self.had_cellular,\
                self.byte_upload, self.byte_download,\
                self.byte_encrypted,\
                len(self.active_apps)






def load_session_data(limit=-1)
    timestream = defaultdict(list)
    f = open("/z/user-study-imc15/PACO/user_session_summary.txt")
    for line in f.readlines():
        (userid, start_time, end_time, session_id) = line.split()
        timestream[userid].append(SessionAttribute(userid, start_time, end_time, session_id)
        

    return timestream


if __name__ == "__main__":

    session_timeline = load_by_user()
    flow_timeline = timestream.load_timeline()
    

