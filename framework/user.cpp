//
//  user.cpp
//  PacketTraceExplorer
//
//  Created by Junxian Huang on 1/26/13.
//  Copyright (c) 2013 Junxian Huang. All rights reserved.
//

#include "framework/user.h"

user::user() {
    start_time = 0;
    last_packet_time = 0;
    tcp_flows.clear();
    last_http_time = 0;
    http_req_stat = new stringstream();
    http_req_stat->str("");
    http_req_stat_size = 0;
}
