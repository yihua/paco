/*
 * config_param.h
 *
 *  Created on: Dec 6, 2013
 *      Author: yihua
 */

#ifndef CONFIG_PARAM_H_
#define CONFIG_PARAM_H_

#include "common/param.h"

#define CONFIG_PARAM_TRACE "trace_type"
#define CONFIG_PARAM_TRACE_DEV "0"
#define CONFIG_PARAM_TRACE_SRV "1"
#define CONFIG_PARAM_TRACE_DEV_SRV "2"

#define CONFIG_PARAM_CONTEXT "context_type"
#define CONFIG_PARAM_CONTEXT_NO "0"
#define CONFIG_PARAM_CONTEXT_YES "1"

#define CONFIG_PARAM_TRACE_LIST "trace_list"

class ConfigParam: private Param {
private:
public:
	ConfigParam();
	void configContextType(string s);
	void configTraceList(string s);
	void configTraceType(string s);

	void copyConfigParam(Param param);

	string getContextType();
	string getTraceList();
	string getTraceType();
};

#endif /* CONFIG_PARAM_H_ */
