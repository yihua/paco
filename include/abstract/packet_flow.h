/*
 * packet_flow.h
 *
 *  Created on: Apr 23, 2015
 *      Author: Yihua
 */

#ifndef _PACO_PACKET_FLOW_H
#define _PACO_PACKET_FLOW_H

#include "common/basic.h"
#include "common/io.h"
#include "common/stl.h"
#include "proto/tcp_ip.h"
#include "proto/http.h"

#include "abstract/packet.h"

class PacketFlow {
    list<Packet*> packetSeries;
    list<Packet*>::iterator pktIter;
    map<string, double> lastLabelTime;
    map<string, double>::iterator iter;
    map<string, bool> toProcess;
    int networkType;
    double currTimestamp;

    bool deleteFlag;
public:
    PacketFlow();
    void updatePacketFlow(int networkType, string label, string flowIndex, double timestamp, int payloadSize, int direction);
    void computeEnergy(bool computeAll);
};

#endif /* _PACO_PACKET_FLOW_H */
