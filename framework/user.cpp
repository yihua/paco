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
    currFolder = "";
    lastFolder = "";
    start_time = -1.0;
    last_packet_time = 0;
    last_epkt_time = 0;
    last_packet_dir = -1;
    tcp_flows.clear();
    last_http_time = 0;
    http_req_stat = new stringstream();
    http_req_stat->str("");
    http_req_stat_size = 0;
    last_app = "";
    last_flow_index = "";
    last_flow_valid = false;
    last_payload = -1;
    energy_bin_start = 0.0;
    conn_d_data_size = 0;
    conn_u_data_size = 0;

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

    lastCycleStartTime = DEFAULT_CYCLE_START;
    //resetCycleStat(currentTime);
}

string User::getFolder() {
    return (lastFolder + "\n" + currFolder);
}

void User::resetCycleStat(double currentTime) {
    cycleTransferTime[0] = 0.0;
    cycleTransferTime[1] = 0.0;
    cycleTailTime[0] = 0.0;
    cycleTailTime[1] = 0.0;
    cycleTransferEnergy[0] = 0.0; 
    cycleTransferEnergy[1] = 0.0; 
    cycleTailEnergy[0] = 0.0; 
    cycleTailEnergy[1] = 0.0; 
    cycleTCPTransferEnergy[0] = 0.0;
    cycleTCPTransferEnergy[1] = 0.0;
    while (lastCycleStartTime + CYCLE_TIME < currentTime) {
        lastCycleStartTime += CYCLE_TIME;
    }
}

bool User::isInCycle(double currentTime) {
    if (currentTime - lastCycleStartTime <= CYCLE_TIME) 
        return true;
    return false;
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

void User::resetEnergyStat(double currTs) {
    appEnergy.clear();
    appUpBytes.clear();
    appDownBytes.clear();
    appLastTime.clear();
    energy_bin_start = currTs;
}
