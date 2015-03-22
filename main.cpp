#include <iostream>
#include "paco.h"

// Other option: "/z/uplink-bufferbloat"
#define ROOT_FOLDER "/z/user-study-imc15/"

using namespace std;

int main() {
	// will concatenate
	string traceList(ROOT_FOLDER "PACO/pcaplistallsort");
	ConfigParam param;
	param.configTraceList(traceList);
	param.configContextType(CONFIG_PARAM_TRACE_DEV);
	param.configTraceType(CONFIG_PARAM_TRACE_DEV);
	param.configMeasumentTask(CONFIG_PARAM_MEASUREMENT_TCPFLOW);
	param.configCountCycle("1000");

	Result* result = new Result();

	string path(ROOT_FOLDER "PACO/concurrency_result.txt");
	string test_flow(ROOT_FOLDER "PACO/flow_summary.txt");
	string test_rate(ROOT_FOLDER "PACO/rate_summary.txt");
	string test_session(ROOT_FOLDER "PACO/session_summary.txt");

    // We effectively control what data is collected by commenting/uncommenting these
	result->addResultFile(1, path);
	result->addResultFile(2, test_flow);
	result->addResultFile(3, test_rate);
	result->addResultFile(4, test_session);

	PacketAnalyzer analyzer;
	analyzer.setConfigParam(param);
	analyzer.setResult(result);
	analyzer.checkSystem();
	analyzer.run();

	return 0;
}
