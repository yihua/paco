/*
 * traffic_abstract.h
 *
 *  Created on: Dec 7, 2013
 *      Author: yihua
 */

#ifndef TRAFFIC_ABSTRACT_H_
#define TRAFFIC_ABSTRACT_H_

#include "common/basic.h"
#include "common/stl.h"

#include "framework/measure_task.h"

class TrafficAbstract {
private:
	vector<MeasureTask> mMeasureTask;
public:
	TrafficAbstract();

	void runMeasureTask(const struct pcap_pkthdr *header, const u_char *pkt_data);
};

#endif /* TRAFFIC_ABSTRACT_H_ */
