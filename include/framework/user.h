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
#include "abstract/packet_flow.h"

#define USER_SESSION_IDLE 60.0 // s
#define USER_RATE_BIN 1.0 // s
#define ENERGY_BIN 1.0 // s

#define CYCLE_TIME 86400 // s, 1 day
#define DEFAULT_CYCLE_START 1346472000

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
    double last_epkt_time;
    int last_packet_dir;
    double energy_bin_start;
    int last_bin_network;
    string last_app;
    string last_flow_index;
    bool last_flow_valid;
    double cc_start;
    double last_cc_sample_time;
    int last_payload;

    double lastCycleStartTime;
    double cycleTransferTime[2], cycleTailTime[2], cycleTransferEnergy[2], cycleTailEnergy[2], cycleTCPTransferEnergy[2], cycleTCPTailEnergy[2];

    double bw_bin_ul_start_time, bw_bin_ul_end_time;
    uint64 bw_bin_ul_ip_all, bw_bin_ul_ip_payload; 
    uint64 bw_bin_ul_tcp_all, bw_bin_ul_tcp_payload, bw_bin_ul_udp_all, bw_bin_ul_udp_payload;

    double bw_bin_dl_start_time, bw_bin_dl_end_time;
    uint64 bw_bin_dl_ip_all, bw_bin_dl_ip_payload; 
    uint64 bw_bin_dl_tcp_all, bw_bin_dl_tcp_payload, bw_bin_dl_udp_all, bw_bin_dl_udp_payload;

    double session_start_time, session_end_time;
    uint64 session_ul_ip_all, session_ul_ip_payload; 
    uint64 session_ul_tcp_all, session_ul_tcp_payload, session_ul_udp_all, session_ul_udp_payload;

    uint64 session_dl_ip_all, session_dl_ip_payload; 
    uint64 session_dl_tcp_all, session_dl_tcp_payload, session_dl_udp_all, session_dl_udp_payload;    

    bool is_sample;

    map<string, TCPFlow*> tcp_flows;
    PacketFlow tcpPacketFlow, appPacketFlow;


    map<string, double> appEnergy;
    map<string, double> appLastTime;
    map<string, int> appUpBytes;
    map<string, int> appDownBytes;
    map<string, string> appTimeLog;
    map<string, double> appTime;

    double last_http_time;
    stringstream* http_req_stat;
    int http_req_stat_size;

    User();
    bool isInCycle(double currentTime);
    void resetCycleStat(double currentTime);
    void resetRateStat(int dir);
    void resetSessionStat();
    void resetEnergyStat(double currTs);
};

#endif /* defined(__PacketTraceExplorer__user__) */
