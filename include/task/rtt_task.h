/*
 * rtt_task.h
 *
 *  Created on: Dec 8, 2013
 *      Author: yihua
 */

#ifndef RTT_TASK_H_
#define RTT_TASK_H_

#include "framework/measure_task.h"

class RTTTask: public MeasureTask {
public:
	void procPacket(const TrafficAbstract *abstract, const struct pcap_pkthdr *header, const u_char *pkt_data);
};

#endif /* RTT_TASK_H_ */
