#include <iostream>
#include "framework.h"

using namespace std;

int main() {
	string traceList("/home/yihua/workspace/PACO/traceList");
	ConfigParam param;
	param.configTraceList(traceList);
	param.configContextType(CONFIG_PARAM_TRACE_DEV);
	param.configMeasumentTask(CONFIG_PARAM_MEASUREMENT_TCPFLOW);

	PacketAnalyzer analyzer;
	analyzer.setConfigParam(param);
	analyzer.checkSystem();
	analyzer.run();

	return 0;
}
