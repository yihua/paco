/*
 * common/param.cpp
 * PACO
 *
 * Created by: Yihua Guo, 12/05/2013
 *
 * Function: implementation of Param
 *
 */

#include "common/param.h"

Param::Param() {
}

void Param::copyParam(Param param) {
	map<string, string>::iterator it;
	for (it = this->param.begin(); it != this->param.end(); it++) {
		param.put(it->first, it->second);
	}
}

string Param::get(string key) {
	return param[key];
}

void Param::put(string key, string value) {
	param.insert(pair<string, string>(key, value));
}

