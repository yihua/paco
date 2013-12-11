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
int femode=0;
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
int getCurrentFuturePast(double targettime, int tpnt, vector<double>* &res, int &pointer){
    for (; tpnt<tsQueue.size() && tsQueue.at(tpnt)<targettime; tpnt++);
    pointer=tpnt;
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
    bool nodata=false;
    for (int i=0;i<=past_week;i++) {
      for (int j=0;j<=past_day;j++){
          if (i==0 && j==0){
          //today
            if (getTodayPast(tpnt, res)==-1)  {nodata=true; break;};
          }
          else {
          //pastdays

             //limited feature for femode 0
             if (femode==0 && i>0 && j!=0) continue;

             double targetTimeStamp=tsQueue.at(tpnt)-i*WEEKSPAN-j*DAYPAN;
             int startpoint=0;
             if (tsPointers[i][j]>=0)
               startpoint=tsPointers[i][j];
             if (getCurrentFuturePast(targetTimeStamp, startpoint, res, tsPointers[i][j])) {nodata=true; break;};

          }

      }
      if (nodata) break;
    }
    return 0;
}

void rycQueue(){
    int quedelta=tsPointers[past_week+1][past_day+1]-timestamp_num;
    if (quedelta>0){
        for (int i=0;i<quedelta;i++)
          tsQueue.pop_front();

        for (int i=0;i<=past_week;i++)
          for (int j=0;j<=past_day;j++)
            tsPointers[i][j]-=quedelta;
    }

}

int fullVectorSize(){
    if (femode==0)
      return ((past_week+past_day)*2+1)*timestamp_num;
    if (femode==1)
      return ((past_week+1)*(past_day+1)*2-1)*timestamp_num;
    return 0;
}

bool isFullVector(vector<double>* &res){
    if (res->size()<fullVectorSize()) return false;
    return true;
}

void featureExtraction(char* fefilename, int tnum, int pweek, int pday, int mode){
//fefilename: raw data file name
//tnum: number of timestamps to be counted in feature
//pweek: number of past weeks to be counted in feature
//pday: number of past days to be counted in feature
//mode: [0|1], 0 means extracting features excepting the ones in past days in past weeks, 1 means including them
    timestamp_num=tnum;
    past_week=pweek;
    past_day=pday;
    femode=mode;
    ifstream finFE(fefilename);
    ofstream foutFE("output");
    char strFE[3000];

    //clear tsPointers
    for (int i=0;i<=past_week;i++)
      for (int j=0;j<=past_day;j++)
        tsPointers[i][j]=0;

    printf("%d\n",fullVectorSize());

    res=new vector<double>();

    double lastOne=-1;
    while (finFE.getline(strFE,3000)){
        double timestamp;
        res->clear();
        sscanf(strFE,"%lf",&timestamp);
        printf("%lf\n",timestamp);
        tsQueue.push_back(timestamp);
        getFeatureVector(tsQueue.size()-1,res);


 /*    for (int i=0;i<=past_week;i++)
      for (int j=0;j<=past_day;j++)
        printf("%d ",tsPointers[i][j]);
     cout<<endl;
*/
       if (isFullVector(res)){
           if (lastOne!=-1)
              res->push_back(timestamp-lastOne);
           for (int i=0;i<res->size();i++)
             foutFE<<res->at(i)<<" ";
            foutFE<<endl;
       }
       lastOne=timestamp;
       rycQueue();

    }
    finFE.close();
    foutFE.close();

}
