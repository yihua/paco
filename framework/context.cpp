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
    networkType = -1;
    currFolder = "";
    lastFolder = "";
    //fgAppLastLine = "";
    //tmpTime = -1;
}

void Context::printFgApp(string uid) {
    set<string>::iterator it;
    for (it = fgApp[uid].begin(); it != fgApp[uid].end(); it++) {
        cout << *it << " | ";
    }
    cout << endl;
}


void Context::updateForegroundApp(string uid, double ts) {
    if (tmpTime.find(uid) != tmpTime.end() ) {
        if (ts < double(tmpTime[uid])) {
            //cout << ts << " " << tmpTime[uid] << endl;
            return;
        }
    } else {
        tmpTime[uid] = -1;
        fgTime[uid] = -1;
        string tmpFn(FG_PREFIX);
        infile[uid] = new ifstream(tmpFn.append(uid).c_str());
        fgAppLastLine[uid] = "";
    }

    if (fgAppLastLine[uid].length() > 0) {
        //cout << uid << " " << fgTime[uid] <<": ";
        //printFgApp(uid);

        istringstream isst(fgAppLastLine[uid]);
        isst >> tmpUID >> tmpT >> tmpAppName;
        
        if (double(tmpT) > ts) {
            return;
        }

        //cout << uid << " " << fgTime[uid] <<": ";
        //printFgApp(uid);

        tmpTime[uid] = tmpT;
        fgTime[tmpUID] = tmpTime[uid];

        //if (fgApp.find[tmpUID] == fgApp.end()) {
        //    fgApp[tmpUID] = new set<string>();
        //}

        fgApp[tmpUID].clear();
        fgApp[tmpUID].insert(tmpAppName);
    }

    while (std::getline(*(infile[uid]), fgAppLastLine[uid])) {
        //cout << uid << " read lines .... " << ts << " | "<< fgAppLastLine[uid] << endl;
        istringstream iss(fgAppLastLine[uid]);
        iss >> tmpUID >> tmpT >> tmpAppName;
        //cout << tmpUID << " " <<  tmpT << " " << tmpAppName;
        
        if (double(tmpT) > ts) {
            return;
        }        

        tmpTime[uid] = tmpT;

        //cout << tmpTime[uid] << endl;

        if (fgTime.find(tmpUID) == fgTime.end()) {
            fgTime[tmpUID] = tmpTime[uid];
            //fgApp[tmpUID] = new set<string>();
            fgApp[tmpUID].clear();
            fgApp[tmpUID].insert(tmpAppName);
        } else {
            if (fgTime[tmpUID] == tmpTime[uid]) {
                fgApp[tmpUID].insert(tmpAppName);
                //cout << "add record" << endl;
            } else {
                if (ts >= tmpTime[uid]) {
                    //cout << uid << " " << fgTime[uid] <<": ";
                    //printFgApp(uid);

                    fgTime[tmpUID] = tmpTime[uid];
                    fgApp[tmpUID].clear();
                    fgApp[tmpUID].insert(tmpAppName);
                    //cout << "continue --------------->" << endl;
                } else {
                    //cout << "return************************" << endl;
                    return;
                }
            }
        }
    }
}

bool Context::isForeground(string uid, string appName) {
    if (fgApp.find(uid) == fgApp.end()) {
        return false;
    }

    if (fgApp[uid].find(appName) == fgApp[uid].end()) {
        return false;
    }
    return true;
}

void Context::setEtherLen(int etherlen){
    ETHER_HDR_LEN = etherlen;
}

int Context::getNetworkType() {
    return networkType;
}

void Context::setNetworkType(int type) {
    this->networkType = type;
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

void Context::setUserID(string s) {
	userID = s;
}

string Context::getUserID() {
	return userID;
}

bool Context::parseScreenOn(string s) {
	int pos1 = s.find(" ");
	if (s.substr(pos1+1,2).compare("ON") == 0) {
		return true;
	} else {
		return false;
	}
}

void Context::updateContext(double ts) {
	bool active;
	while (ts > screen_time) {
		screenOn = parseScreenOn(screen_line);

		if (getline(screen_context, screen_line)) {
			screen_time = getTimestamp(screen_line);
		} else {
			break;
		}
	}

	while (ts > proc_time) {
		if (isProcessLine(proc_line)) {
			active = isImportanceFg(proc_line);
			string appName = getAppName(proc_line);
			if (active) {
				foregroundApp.insert(appName);
			} else {
				if (isForeground(appName)) {
					foregroundApp.erase(appName);
				}
			}
		}

		if (getline(proc_context, proc_line)) {
			proc_time = getTimestamp(proc_line);
		} else {
			break;
		}
	}
}

void Context::updateFile(string s) {
	if (screen_context != NULL) {
		screen_context.close();
	}

	if (proc_context != NULL) {
		proc_context.close();
	}

	screen_context.open((s + "screen_events").c_str());
	proc_context.open((s + "active_process").c_str());

	screenOn = false;
	foregroundApp.clear();

	if (getline(screen_context, screen_line)) {
		screen_time = getTimestamp(screen_line);
	} else {
		return;
	}

	if (getline(proc_context, proc_line)) {
		proc_time = getTimestamp(proc_line);
	} else {
		return;
	}
}

double Context::getTimestamp(string s) {
	int pos1 = s.find("[");
	int pos2 = s.find("]");

	return atof(s.substr(pos1+1, pos2-pos1-1).c_str());
}

string Context::getAppName(string s) {
	int pos1 = s.find(" ");
	int pos2 = s.find(" ", pos1+1);

	return s.substr(pos1+1, pos2-pos1-1);
}

bool Context::isProcessLine(string s) {
	int pos1 = s.find(" ");
	pos1 = s.find(" ", pos1+1);
	pos1 = s.find(" ", pos1+1);
	if (pos1 < 0) {
		return false;
	} else {
		return true;
	}
}

bool Context::isImportanceFg(string s) {
	int pos1 = s.find(" ");
	pos1 = s.find(" ", pos1+1);
	int pos2 = s.find(" ", pos1+1);

	if (s.substr(pos1+1, pos2-pos1-1).compare("100") == 0) {
		return true;
	} else {
		return false;
	}
}

bool Context::isForeground(string appName) {
	if (foregroundApp.find(appName) != foregroundApp.end()) {
		return true;
	}
	return false;
}

bool Context::isScreenOn() {
	return screenOn;
}

string Context::getFolder() {
	return (lastFolder + "\n" + currFolder);
}

void Context::setFolder(string s) {
	lastFolder = currFolder;
	currFolder = s;
}

void Context::incrPacketNo() {
	packetNo++;
}

int Context::getPacketNo() {
	return packetNo;
}

void Context::setPacketNo(int i) {
	packetNo = i;
}
