#include <iostream>
#include "framework.h"

using namespace std;

int main() {
	string traceList("/home/yihua/testlist");
	ConfigParam param;
	param.configTraceList(traceList);

	PacketAnalyzer analyzer;
	analyzer.config(param);
	analyzer.checkSystem();
	analyzer.run();

	return 0;
}
