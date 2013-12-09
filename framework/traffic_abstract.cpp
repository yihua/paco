/*
 * traffic_abstract.cpp
 *
 *  Created on: Dec 7, 2013
 *      Author: yihua
 */

#include "framework/traffic_abstract.h"
#include "framework/context.h"

TrafficAbstract::TrafficAbstract() {

}

void TrafficAbstract::runMeasureTask(Context traceCtx, const struct pcap_pkthdr *header, const u_char *pkt_data) {
	vector<MeasureTask>::iterator it;
	for (it = mMeasureTask.begin(); it != mMeasureTask.end(); it++) {
		it->procPacket(this, header, pkt_data);
	}
}
