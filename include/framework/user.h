//
//  user.h
//  PacketTraceExplorer
//
//  Created by Junxian Huang on 1/26/13.
//  Copyright (c) 2013 Junxian Huang. All rights reserved.
//

#ifndef __PacketTraceExplorer__user__
#define __PacketTraceExplorer__user__

#include <map>

#include "abstract/tcp_flow.h"


class user {
public:
    double start_time;
    double last_packet_time;
    map<u_short, TCPFlow*> tcp_flows;

    user();

};

#endif /* defined(__PacketTraceExplorer__user__) */
