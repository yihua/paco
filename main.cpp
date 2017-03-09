#include <iostream>
#include "paco.h"

// Other option: "/z/uplink-bufferbloat"
#define ROOT_FOLDER "/nfs/rome2/david/paco/"

using namespace std;

int main(int argc, char** argv) {
	// will concatenate
	if (argc != 2) {
		cout << "Usage: ./paco [userID]" << endl;
		return 0;
	} else {
		cout << "User ID: " << argv[1] << endl; 
	}
	string traceList(ROOT_FOLDER "PACO/pcapsort");
	ConfigParam param;
	param.configTraceList(traceList);
	param.configContextType(CONFIG_PARAM_TRACE_DEV);
	param.configTraceType(CONFIG_PARAM_TRACE_DEV_PCAP_MAPPING); //CONFIG_PARAM_TRACE_DEV_PCAP);
	param.configMeasumentTask(CONFIG_PARAM_MEASUREMENT_TCPFLOW);
	param.configCountCycle("1000");

	Result* result = new Result();

	string path(ROOT_FOLDER "PACO/concurrency_result_");
	string test_flow(ROOT_FOLDER "PACO/flow_summary_");
	string test_rate(ROOT_FOLDER "PACO/rate_summary_");
	string test_session(ROOT_FOLDER "PACO/session_summary_");
	string test_power(ROOT_FOLDER "PACO/energy_summary_");
    string test_val(ROOT_FOLDER "PACO/validate_");
    string rtt_result(ROOT_FOLDER "PACO/rtt_");
	path += string(argv[1]);
	test_flow += string(argv[1]);
	test_rate += string(argv[1]);
	test_session += string(argv[1]);
	test_power += string(argv[1]);
	test_val += string(argv[1]);
	rtt_result += string(argv[1]);

    // We effectively control what data is collected by commenting/uncommenting these
	result->addResultFile(1, path, -1);
	result->addResultFile(2, test_flow, -1);
	result->addResultFile(3, test_rate, -1);
	result->addResultFile(4, test_session, -1);
	result->addResultFile(5, test_power, -1);
    result->addResultFile(6, test_val, 200);
    result->addResultFile(7, rtt_result, -1);

	PacketAnalyzer analyzer;
	analyzer.setConfigParam(param);
	analyzer.setResult(result);
	analyzer.checkSystem();
	analyzer.run(argv[1]);

	return 0;
}
