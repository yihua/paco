/*
 * framework/context.h
 * PACO
 *
 * Created by: Qi Alfred Chen, 12/09/2013
 *
 */

#ifndef _PACO_CONTEXT_H
#define _PACO_CONTEXT_H

#include "common/stl.h"
#include "common/io.h"

#define FG_PREFIX "/nfs/beirut1/userstudy/2nd_round/active/active_fg_sort_"

class Context {
private:
	int packetNo;

	vector<string> appNameMap;
	string userID;
	int ETHER_HDR_LEN;
    int networkType;
	ifstream screen_context, proc_context;
	string screen_line, proc_line;
	double screen_time, proc_time;
	bool screenOn;
	set<string> foregroundApp;

    map<string, ifstream*> infile;

    string tmpLine, tmpUID, tmpAppName;
    double tmpT;
    int tmpCode;
    map<string, double> tmpTime;
    //istringstream iss;
    //map<string, set<string> > fgApp;
    map<string, map<string, int> > appStatus;

    //map<string, int> fgTime;
    map<string, string> appLastLine;

    void printFgApp(string uid);
	double getTimestamp(string s);
	string getAppName(string s);

    /* Appears to be whether the app occupies the foreground 
     * physically?
     */
	bool isImportanceFg(string s);
	bool isProcessLine(string s);
	bool parseScreenOn(string s);
public:
    string currFolder, lastFolder;
    
    const static int NETWORK_TYPE_WIFI = 0;
    const static int NETWORK_TYPE_CELLULAR = 1;

    Context();
    //void updateForegroundApp(string uid, double ts);
    void updateAppStatus(string uid, double ts);
    int getAppStatus(string uid, string appName);
    //bool isForeground(string uid, string appName);
    void setEtherLen(int etherlen);
    int getNetworkType();
    void setNetworkType(int type);
    void setUserID(string s);
    int getEtherLen();
    vector<string> getAppNameMap();
    void addAppName(string appname);
    void clearAppNameMap();

    // Get the app in the specified position on the map
    string getAppNameByIndex(int index);
    string getUserID();
    void updateContext(double ts);

    // Given the filename, load the screen events
    void updateFile(string s);
    bool isScreenOn();
    bool isForeground(string appName);
    string getFolder();
    string getCurrFolder();
    void setFolder(string s);
    
    void incrPacketNo();
    int getPacketNo();
    void setPacketNo(int i);
};

#endif /* _PACO_CONTEXT_H */
