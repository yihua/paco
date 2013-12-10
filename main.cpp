#include <iostream>
#include "framework.h"

using namespace std;

int main() {
	string traceList("/home/alfred/courses/545/data/traceList");
	ConfigParam param;
	param.configTraceList(traceList);

	PacketAnalyzer analyzer;
	analyzer.config(param);
	analyzer.checkSystem();
	analyzer.run();

	return 0;
}
