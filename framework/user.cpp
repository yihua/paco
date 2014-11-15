//
//  user.cpp
//  PacketTraceExplorer
//
//  Created by Junxian Huang on 1/26/13.
//  Copyright (c) 2013 Junxian Huang. All rights reserved.
//

#include "framework/user.h"

User::User() {
	//cout << "user init" << endl;
    start_time = -1.0;
    last_packet_time = 0;
    tcp_flows.clear();
    last_http_time = 0;
    http_req_stat = new stringstream();
    http_req_stat->str("");
    http_req_stat_size = 0;

    bw_bin_ul_start_time = -1.0;
    bw_bin_ul_end_time = -1.0;
    bw_bin_ul_ip_all = 0;
    bw_bin_ul_ip_payload = 0; 
    bw_bin_ul_tcp_all = 0;
    bw_bin_ul_tcp_payload = 0;
    bw_bin_ul_udp_all = 0;
    bw_bin_ul_udp_payload = 0;

    bw_bin_dl_start_time = -1.0;
    bw_bin_dl_end_time = -1.0;
    bw_bin_dl_ip_all = 0;
    bw_bin_dl_ip_payload = 0; 
    bw_bin_dl_tcp_all = 0;
    bw_bin_dl_tcp_payload = 0;
    bw_bin_dl_udp_all = 0;
    bw_bin_dl_udp_payload = 0;

    session_start_time = -1.0;
	session_end_time = -1.0;
    session_ul_ip_all = 0;
    session_ul_ip_payload = 0; 
    session_ul_tcp_all = 0;
    session_ul_tcp_payload = 0;
    session_ul_udp_all = 0;
    session_ul_udp_payload = 0;

    session_dl_ip_all = 0;
    session_dl_ip_payload = 0; 
    session_dl_tcp_all = 0;
    session_dl_tcp_payload = 0;
    session_dl_udp_all = 0;
    session_dl_udp_payload = 0;
}

void User::resetRateStat(int dir) {
	if (dir == 0) {
		bw_bin_ul_ip_all = 0;
	    bw_bin_ul_ip_payload = 0; 
	    bw_bin_ul_tcp_all = 0;
	    bw_bin_ul_tcp_payload = 0;
	    bw_bin_ul_udp_all = 0;
	    bw_bin_ul_udp_payload = 0;
	    return;
	}

	if (dir == 1) {
	    bw_bin_dl_ip_all = 0;
	    bw_bin_dl_ip_payload = 0; 
	    bw_bin_dl_tcp_all = 0;
	    bw_bin_dl_tcp_payload = 0;
	    bw_bin_dl_udp_all = 0;
	    bw_bin_dl_udp_payload = 0;
	    return;
    }
}

void User::resetSessionStat() {
    session_ul_ip_all = 0;
    session_ul_ip_payload = 0; 
    session_ul_tcp_all = 0;
    session_ul_tcp_payload = 0;
    session_ul_udp_all = 0;
    session_ul_udp_payload = 0;

    session_dl_ip_all = 0;
    session_dl_ip_payload = 0; 
    session_dl_tcp_all = 0;
    session_dl_tcp_payload = 0;
    session_dl_udp_all = 0;
    session_dl_udp_payload = 0;
}