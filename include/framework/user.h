//
//  user.h
//  PacketTraceExplorer
//
//  Created by Junxian Huang on 1/26/13.
//  Copyright (c) 2013 Junxian Huang. All rights reserved.
//

#ifndef __PacketTraceExplorer__user__
#define __PacketTraceExplorer__user__

#include "common/stl.h"

#include "abstract/tcp_flow.h"

struct string_less {
    bool operator() (const string& lhs, const string& rhs) const {
        return lhs.compare(rhs) < 0;
    }
};

class user {
public:
	string userID;
    double start_time;
    double last_packet_time;
    double cc_start;
    double last_cc_sample_time;
    bool is_sample;

    map<string, TCPFlow*> tcp_flows;
    map<string, string> appTimeLog;
    map<string, double> appTime;

    double last_http_time;
    stringstream* http_req_stat;
    int http_req_stat_size;

    user();

};

#endif /* defined(__PacketTraceExplorer__user__) */
