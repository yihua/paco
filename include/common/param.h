/*
 * common/param.h
 * PACO
 *
 * Created by: Yihua Guo, 12/05/2013
 *
 * Function: data structure (key-value pair) for parameters
 *
 */

#ifndef _PACO_PARAM_H
#define _PACO_PARAM_H

#include "common/stl.h"

class Param {
private:
	map<string, string> param;
public:
	Param();
	void copyParam(Param param);
	string get(string key);
	void put(string key, string value);
};

#endif /* _PACO_PARAM_H */
