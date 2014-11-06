#include <iostream>
#include "paco.h"

using namespace std;

int main() {
	string traceList("/home/yhguo/PACO/pcaplistallsort");
	ConfigParam param;
	param.configTraceList(traceList);
	param.configContextType(CONFIG_PARAM_TRACE_DEV);
	param.configMeasumentTask(CONFIG_PARAM_MEASUREMENT_TCPFLOW);
	param.configCountCycle("1000");

	Result* result = new Result();
	string path("/home/yhguo/PACO/concurrency_result.txt");
	result->addResultFile(1, path);
	PacketAnalyzer analyzer;
	analyzer.setConfigParam(param);
	analyzer.setResult(result);
	analyzer.checkSystem();
	analyzer.run();

	return 0;
}
