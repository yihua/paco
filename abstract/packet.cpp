/*
 * packet.cpp
 *
 *  Created on: Apr 23, 2015
 *      Author: yihua
 */

#include "abstract/packet.h"

Packet::Packet(string label, string flowIndex, double timestamp, int payloadSize, int direction) {
    this->label = label;
    this->flowIndex = flowIndex;
    this->processed = false;
    this->timestamp = timestamp;
    this->payloadSize = payloadSize;
    this->direction = direction;
}
