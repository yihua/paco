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

#define USER_SESSION_IDLE 60.0 // s
#define USER_RATE_BIN 1.0 // s

struct string_less {
    bool operator() (const string& lhs, const string& rhs) const {
        return lhs.compare(rhs) < 0;
    }
};

class User {
public:
	string userID;
    double start_time;
    double last_packet_time;
    double cc_start;
    double last_cc_sample_time;

    double bw_bin_start_time;
    uint64 bw_bin_ip_all, bw_bin_ip_payload; 
    uint64 bw_bin_tcp_all, bw_bin_tcp_payload, bw_bin_udp_all, bw_bin_udp_payload;

    double session_start_time, session_end_time;
    uint64 session_ip_all, session_ip_payload; 
    uint64 session_tcp_all, session_tcp_payload, session_udp_all, session_udp_payload;    

    bool is_sample;

    map<string, TCPFlow*> tcp_flows;
    map<string, string> appTimeLog;
    map<string, double> appTime;

    double last_http_time;
    stringstream* http_req_stat;
    int http_req_stat_size;

    User();
    void resetRateStat();
    void resetSessionStat();
};

#endif /* defined(__PacketTraceExplorer__user__) */
