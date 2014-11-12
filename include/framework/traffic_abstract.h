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
#include "framework/context.h"
#include "framework/result.h"
#include "param/config_param.h"

class TrafficAbstract {
private:
//use int * since error "error: cannot allocate an object of abstract type ‘MeasureTask’"
	vector<int *> mMeasureTask;
public:
//	TrafficAbstract();
	virtual void runMeasureTask(Result* result, Context& traceCtx, const struct pcap_pkthdr *header, const u_char *pkt_data)=0;
	virtual void runCleanUp(Result* result) = 0;
};

#endif /* TRAFFIC_ABSTRACT_H_ */
