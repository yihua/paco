/*
 * common/output.h
 * PACO
 *
 * Created by: Yihua Guo, 03/04/2013
 *
 * Function: store output to files
 *
 */

#ifndef _PACO_OUTPUT_H
#define _PACO_OUTPUT_H

#include "common/stl.h"
#include "common/io.h"

#define BLOCK_SIZE 10240

class OutputFile {
public:
	static void append(stringstream* ss, int& size, const double ts, const string append_s, const string file_name, const string user_id) {
		if (ts > 0.1)
			*ss << int(ts*1000.0);
		*ss << append_s;
		string f_name(file_name);
		f_name += user_id;
		size += (17 + append_s.length());
		if (size > BLOCK_SIZE) {
			ofstream f_output(f_name.c_str(), ios::app);
			f_output << ss->str();
			f_output.close();
			ss->clear();//clear any bits set
			ss->str(std::string());
			size = 0;
		}
	}
};

#endif /* _PACO_OUTPUT_H */
