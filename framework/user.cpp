//
//  user.cpp
//  PacketTraceExplorer
//
//  Created by Junxian Huang on 1/26/13.
//  Copyright (c) 2013 Junxian Huang. All rights reserved.
//

#include "framework/user.h"

User::User() {
	cout << "user init" << endl;
    start_time = -1.0;
    last_packet_time = 0;
    tcp_flows.clear();
    last_http_time = 0;
    http_req_stat = new stringstream();
    http_req_stat->str("");
    http_req_stat_size = 0;

    bw_bin_start_time = -1.0;
    bw_bin_ip_all = 0;
    bw_bin_ip_payload = 0; 
    bw_bin_tcp_all = 0;
    bw_bin_tcp_payload = 0;
    bw_bin_udp_all = 0;
    bw_bin_udp_payload = 0;

    session_start_time = -1.0;
	session_end_time = -1.0;
    session_ip_all = 0;
    session_ip_payload = 0; 
    session_tcp_all = 0;
    session_tcp_payload = 0;
    session_udp_all = 0;
    session_udp_payload = 0;
}

void User::resetRateStat() {
    bw_bin_ip_all = 0;
    bw_bin_ip_payload = 0; 
    bw_bin_tcp_all = 0;
    bw_bin_tcp_payload = 0;
    bw_bin_udp_all = 0;
    bw_bin_udp_payload = 0;
}

void User::resetSessionStat() {
    session_ip_all = 0;
    session_ip_payload = 0; 
    session_tcp_all = 0;
    session_tcp_payload = 0;
    session_udp_all = 0;
    session_udp_payload = 0;
}