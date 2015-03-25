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

class Context {
private:
	vector<string> appNameMap;
	string userID;
	int ETHER_HDR_LEN;
	ifstream screen_context, proc_context;
	string screen_line, proc_line;
	double screen_time, proc_time;
	bool screenOn;
	set<string> foregroundApp;

	double getTimestamp(string s);
	string getAppName(string s);

    /* Appears to be whether the app occupies the foreground 
     * physically?
     */
	bool isImportanceFg(string s);
	bool isProcessLine(string s);
	bool parseScreenOn(string s);
public:
    Context();
    void setEtherLen(int etherlen);
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
};

#endif /* _PACO_CONTEXT_H */
