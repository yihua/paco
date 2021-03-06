/*
 * framework/result.h
 * PACO
 *
 * Created by: Yihua Guo, 11/03/2014
 *
 */

#ifndef _PACO_RESULT_H
#define _PACO_RESULT_H

#include "common/stl.h"
#include "common/io.h"

class Result {
private:
	map<int, string> result_files;
	map<int, string> result_tmp;
    map<int, int> maxBufSize;
public:
	Result();
	void addResultFile(int tag, string path, int thres);
	void addResultToFile(int tag, char* result);
	void addResultToFile(int tag, string result);
	void flush();
	void openAllResultFiles();
	void closeAllResultFiles();
};

#endif /* _PACO_RESULT_H */
