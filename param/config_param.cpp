/*
 * config_param.cpp
 *
 *  Created on: Dec 6, 2013
 *      Author: yihua
 */

#include "param/config_param.h"

ConfigParam::ConfigParam() {
}

void ConfigParam::copyConfigParam(Param param) {
	copyParam(param);
}

void ConfigParam::configContextType(string s) {
	put(CONFIG_PARAM_CONTEXT, s);
}

void ConfigParam::configTraceList(string s) {
	put(CONFIG_PARAM_TRACE_LIST, s);
}

void ConfigParam::configTraceType(string s) {
	put(CONFIG_PARAM_TRACE, s);
}

string ConfigParam::getContextType() {
	return get(CONFIG_PARAM_CONTEXT);
}

string ConfigParam::getTraceList() {
	return get(CONFIG_PARAM_TRACE_LIST);
}

string ConfigParam::getTraceType() {
	return get(CONFIG_PARAM_TRACE);
}
