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
	string test_power(ROOT_FOLDER "PACO/energy_summary.txt");
    string test_val(ROOT_FOLDER "PACO/validate.txt");

    // We effectively control what data is collected by commenting/uncommenting these
	result->addResultFile(1, path, -1);
	result->addResultFile(2, test_flow, -1);
	result->addResultFile(3, test_rate, -1);
	result->addResultFile(4, test_session, -1);
	result->addResultFile(5, test_power, -1);
    result->addResultFile(6, test_val, 200);

	PacketAnalyzer analyzer;
	analyzer.setConfigParam(param);
	analyzer.setResult(result);
	analyzer.checkSystem();
	analyzer.run();

	return 0;
}
