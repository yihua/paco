/*
 * framework/context.cpp
 * PACO
 *
 * Created by: Qi Alfred Chen, 12/09/2013
 *
 */

#include "framework/context.h"

Context::Context() {
    ETHER_HDR_LEN = -1;
}

void Context::setEtherLen(int etherlen){
    ETHER_HDR_LEN = etherlen;
}

int Context::getEtherLen(){
    return ETHER_HDR_LEN;
}

vector<string> Context::getAppNameMap(){
    return appNameMap;
}

void Context::addAppName(string appname){
    appNameMap.push_back(appname);
}

void Context::clearAppNameMap(){
    appNameMap.clear();
}

string Context::getAppNameByIndex(int index){
//empty if the index is not valid
    if (index <0 || index>=appNameMap.size()) return "";

    return appNameMap.at(index);
}
