/*
 * feature_extraction.cpp
 *
 *  Created on: Dec 10, 2013
 *      Author: Qi Alfred Chen
 */

#include "feature_extraction.h"
using namespace std;

void featureExtraction(char* fefilename){
    ifstream finFE(fefilename);
    char strFE[3000];
    while (finFE.getline(strFE,3000)){
        double timestamp;
        sscanf(strFE,"%lf",&timestamp);
        printf("%lf\n",timestamp);

    }
    finFE.close();

}
