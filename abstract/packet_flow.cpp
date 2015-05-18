/*
 * packet_flow.cpp
 *
 *  Created on: Apr 23, 2015
 *      Author: yihua
 */

#include "framework/context.h"
#include "abstract/packet_flow.h"
#include "model/energy.h"

PacketFlow::PacketFlow() {
    networkType = -1;
}

void PacketFlow::updatePacketFlow(int networkType, string label, string flowIndex, double timestamp, int payloadSize, int direction) {
    if (networkType < 0) {
        this->networkType = networkType;
    } else if (networkType != this->networkType) {
        computeEnergy(true);
        this->networkType = networkType;
    }
    Packet* tmpPkt = new Packet(label, flowIndex, timestamp, payloadSize, direction);
    packetSeries.push_back(tmpPkt);
    lastLabelTime[label] = timestamp;
    currTimestamp = timestamp;
    toProcess[label] = false;
}

void PacketFlow::computeEnergy(bool computeAll) {
    for (iter = lastLabelTime.begin(); iter != lastLabelTime.end(); iter++) {
        if (iter->second > 0 && (computeAll || (currTimestamp - iter->second) > getTailTime(networkType))) {
            toProcess[iter->first] = true;
        }
    }
    deleteFlag = true;
    for (pktIter = packetSeries.begin(); pktIter != packetSeries.end(); ) {
        
    }
}
