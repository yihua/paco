#include <iostream>
#include "framework.h"
#include "feature_extraction.h"
using namespace std;

int main() {
/*	string traceList("/home/alfred/courses/545/data/traceList");
	ConfigParam param;
	param.configTraceList(traceList);
	param.configContextType(CONFIG_PARAM_TRACE_DEV);
	param.configMeasumentTask(CONFIG_PARAM_MEASUREMENT_TCPFLOW);

	PacketAnalyzer analyzer;
	analyzer.setConfigParam(param);
	analyzer.checkSystem();
	analyzer.run();
*/
    featureExtraction("/home/alfred/courses/545/PACO/tslog__353091053663193__com.sina.weibo.servant",10,0,0,0);

	return 0;
}
