/*
 * packet.h
 *
 *  Created on: Apr 23, 2015
 *      Author: Yihua
 */

#ifndef _PACO_PACKET_H
#define _PACO_PACKET_H

#include "common/basic.h"
#include "common/io.h"
#include "common/stl.h"
#include "proto/tcp_ip.h"
#include "proto/http.h"

class Packet {
public:
    double timestamp;
    string label, flowIndex; // could be flow index or application name
    bool processed;
    int payloadSize; // TCP level   
    int direction; // 0 up, 1 down

    Packet(string label, string flowIndex, double timestamp, int payloadSize, int direction);
};

#endif /* _PACO_FLOW_H */
