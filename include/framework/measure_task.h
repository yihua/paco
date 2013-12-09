/*
 * framework/measure_task.h
 * PACO
 *
 * Created by: Yihua Guo, 12/06/2013
 *
 */

#ifndef _PACO_MEASURE_TASK_H
#define _PACO_MEASURE_TASK_H

#include "common/basic.h"
#include "common/stl.h"

class TrafficAbstract;

class MeasureTask {
private:
	string result_file;
public:
	virtual void procPacket(const TrafficAbstract *abstract, const struct pcap_pkthdr *header, const u_char *pkt_data)=0;
};

#endif /* _PACO_MEASURE_TASK_H */
