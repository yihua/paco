/*
 * config_param.h
 *
 *  Created on: Dec 6, 2013
 *      Author: yihua
 */

#ifndef CONFIG_PARAM_H_
#define CONFIG_PARAM_H_

#include "common/param.h"
#include <stdlib.h>

#define CONFIG_PARAM_TRACE "trace_type"
#define CONFIG_PARAM_TRACE_DEV "0" // user study
#define CONFIG_PARAM_TRACE_SRV "1"
#define CONFIG_PARAM_TRACE_DEV_SRV "2"
#define CONFIG_PARAM_TRACE_ATT_SPGW "3"
#define CONFIG_PARAM_TRACE_ATT_ENB "4"

#define CONFIG_PARAM_CONTEXT "context_type"
#define CONFIG_PARAM_CONTEXT_NO "0"
#define CONFIG_PARAM_CONTEXT_YES "1"

#define CONFIG_PARAM_TRACE_LIST "traceList"

#define CONFIG_PARAM_MEASUREMENT "measurement_task"
#define CONFIG_PARAM_MEASUREMENT_TCPFLOW "0"

#define CONFIG_PARAM_COUNT_CYCLE "count_cycle"

class ConfigParam: private Param {
private:
public:
	ConfigParam();
	void configContextType(string s);
	void configTraceList(string s);
	void configTraceType(string s);
	void configMeasumentTask(string s);
	void configCountCycle(string s);

	void copyConfigParam(Param param);

	string getContextType();
	string getTraceList();
	string getTraceType();
	string getMeasumentTask();
	int getCountCycle();
	bool isTraceType(string s);

	static bool isSameTraceType(string a, string b) {
		if (a.compare(b) == 0) {
			return true;
		}
		return false;
	}
};

#endif /* CONFIG_PARAM_H_ */
