/*
 * result.cpp
 *
 *  Created on: Nov 3, 2013
 *      Author: yihua
 */

#include "framework/result.h"

#define MAX_BUF_SIZE 1000000

Result::Result() {
	//result_files = new map<int, ofstream>();
	//result_tmp = new map<int, string>();
}

void Result::addResultFile(int tag, string path) {
	result_files[tag] = path;
	ofstream o;
	o.open(path.c_str());
	o.close();
	result_tmp[tag] = "";
}

void Result::addResultToFile(int tag, char *result) {
	result_tmp[tag] += result;
	if (result_tmp[tag].size() > MAX_BUF_SIZE) {
		ofstream o;
		o.open(result_files[tag].c_str(), ios::out | ios::app);
		o << result_tmp[tag];
		o.close();
		result_tmp[tag].clear();
		//cout << "********" << tag << "********* write to file" << endl;
	}
	//cout << "********" << tag << "********* write to file" << endl;
}

void Result::flush() {
	map<int, string>::iterator it;
        for (it = result_files.begin(); it != result_files.end(); it++) {
	        ofstream o;
		o.open(it->second.c_str(), ios::out | ios::app);        
		o << result_tmp[it->first];
		o.close();
		result_tmp[it->first].clear();
        }
}

void Result::openAllResultFiles() {
}

void Result::closeAllResultFiles() {
//	map<int, ofstream>::iterator it;
//	for (it = result_files.begin(); it != result_files.end(); it++) {
//		it->second.close();
//	}
}

