/*
 * feature_extraction.cpp
 *
 *  Created on: Dec 10, 2013
 *      Author: Qi Alfred Chen
 */

#include "feature_extraction.h"
using namespace std;
#define MAXTIMESTAMPNUM 100
#define MAXPASTDAY 100
#define MAXPASTWEEK 100
#define WEEKSPAN 604800
#define DAYPAN 86400

int past_week=1;
int timestamp_num=2;
int past_day=2;
std::deque<double> tsQueue;
int tsPointers[MAXPASTWEEK+1][MAXPASTDAY+1];
vector<double>* res;

int getTodayPast(int tpnt, vector<double>* &res){
    int ret=0;
    for (int i=tpnt; i>tpnt-timestamp_num; i--){
        if (i<=0) {ret=-1; break;};
        double delta=tsQueue.at(i)-tsQueue.at(i-1);
        res->push_back(delta);
    }
    return ret;
}
int getCurrentFuturePast(double targettime, int tpnt, vector<double>* &res){
    for (; tpnt<tsQueue.size() && tsQueue.at(tpnt)<targettime; tpnt++);
    int ret=0;
    for (int i=tpnt+1; i <= tpnt+timestamp_num; i++){
        if (i >= tsQueue.size()) {ret=-1; break; };
        double delta=tsQueue.at(i)-tsQueue.at(i-1);
        res->push_back(delta);
    }
    for (int i=tpnt; i>tpnt-timestamp_num; i--){
        if (i<=0) {ret=-1; break; };
        double delta=tsQueue.at(i)-tsQueue.at(i-1);
        res->push_back(delta);
    }
    return ret;
}

int getFeatureVector(int tpnt, vector<double>* &res){

    printf("%d\n",tpnt);
    bool nodata=false;
    for (int i=0;i<=past_week;i++) {
      for (int j=0;j<=past_day;j++){
          if (i==0 && j==0){
          //today
            if (getTodayPast(tpnt, res)==-1)  {nodata=true; break;};
          }
          else {
          //pastdays
             double targetTimeStamp=tsQueue.at(tpnt)-i*WEEKSPAN-j*DAYPAN;
             int startpoint=0;
             if (tsPointers[i][j]!=-1)
               startpoint=tsPointers[i][j];
             if (getCurrentFuturePast(targetTimeStamp, startpoint, res)) {nodata=true; break;};
          }

      }
      if (nodata) break;
    }
    return 0;
}

void featureExtraction(char* fefilename){
    ifstream finFE(fefilename);
    ofstream foutFE("output");
    char strFE[3000];

    //clear tsPointers
    for (int i=0;i<=past_week;i++)
      for (int j=0;j<=past_day;j++)
        tsPointers[i][j]=-1;

    res=new vector<double>();

    while (finFE.getline(strFE,3000)){
        double timestamp;
        res->clear();
        sscanf(strFE,"%lf",&timestamp);
        printf("%lf\n",timestamp);
        tsQueue.push_back(timestamp);
        getFeatureVector(tsQueue.size()-1,res);

       for (int i=0;i<res->size();i++)
         foutFE<<res->at(i)<<" ";
        foutFE<<endl;



    }
    finFE.close();
    foutFE.close();

}
