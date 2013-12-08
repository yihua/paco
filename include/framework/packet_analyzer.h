/*
 * framework/packet_analyzer.h
 * PACO
 *
 * Created by: Yihua Guo, 12/05/2013
 *
 */

#ifndef _PACO_PACKET_ANALYZER_H
#define _PACO_PACKET_ANALYZER_H

#include "common/stl.h"
#include "framework/measure_task.h"
#include "param/config_param.h"

class PacketAnalyzer {
private:
	vector<MeasureTask> measureTaskList;
	vector<string> traceList;

	int ETHER_HDR_LEN;

public:
	PacketAnalyzer();

	void checkSystem();
	void config(ConfigParam param);
	void run();
};


#endif /* _PACO_PACKET_ANALYZER_H */
