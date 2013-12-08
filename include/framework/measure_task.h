/*
 * framework/measure_task.h
 * PACO
 *
 * Created by: Yihua Guo, 12/06/2013
 *
 */

#ifndef _PACO_MEASURE_TASK_H
#define _PACO_MEASURE_TASK_H

#include "common/stl.h"

class MeasureTask {
private:
	string result_file;
public:
	MeasureTask();
	virtual ~MeasureTask();

	virtual void procPacket();
};

#endif /* _PACO_MEASURE_TASK_H */
