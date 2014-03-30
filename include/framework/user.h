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


class user {
public:
	string userID;
    double start_time;
    double last_packet_time;
    map<uint64, TCPFlow*> tcp_flows;
    map<string, string> appTimeLog;
    map<string, double> appTime;

    double last_http_time;
    stringstream* http_req_stat;
    int http_req_stat_size;

    user();

};

#endif /* defined(__PacketTraceExplorer__user__) */
