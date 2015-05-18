/*
 * energy.h
 *
 *  Created on: Apr 23, 2015
 *      Author: yihua
 */

#include "model/energy.h"
#include "framework/context.h"


double getTailTime(int networkType) {
    switch (networkType) {
        case Context::NETWORK_TYPE_WIFI:
            return TAIL_TIME_WIFI;
        case Context::NETWORK_TYPE_CELLULAR:
            return TAIL_TIME_LTE;
        default:
            return 0.0;
    }
}

