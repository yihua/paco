/*
 * framework/packet_analyzer.cpp
 * PACO
 *
 * Created by: Yihua Guo, 12/05/2013
 *
 */

#include "framework/packet_analyzer.h"
#include "abstract/flow_abstract.h"

void dispatcher_handler(u_char *c, const struct pcap_pkthdr *header, const u_char *pkt_data) {
	PacketAnalyzer* analyzer = (PacketAnalyzer *) c;
	analyzer->runTrafficAbstract(analyzer->getContext(), header, pkt_data);
}

PacketAnalyzer::PacketAnalyzer() {
}

void PacketAnalyzer::checkSystem() {
	int xx = -1;
#if BYTE_ORDER == LITTLE_ENDIAN
	xx = 0;
#endif
#if BYTE_ORDER == BIG_ENDIAN
	xx = 1;
#endif
	switch (xx) {
		case 0:
			cout << "BYTE_ORDER LITTLE_ENDIAN" << endl;
			break;
		case 1:
			cout << "BYTE_ORDER BIG_ENDIAN" << endl;
			break;
		default:
			cout << "BYTE_ORDER NOT BIG NOT SMALL" << endl;
			break;
	}

	//test uint64
	cout << "Length of uint64 should be 8: " << sizeof(uint64) << endl;
}

void PacketAnalyzer::config() {
	ifstream trace_list(mConfigParam.getTraceList().c_str());
	string s;
	while (getline(trace_list, s)) {
		mTraceList.push_back(s);
	}

	//measurement type
	if (mConfigParam.getMeasumentTask().compare(CONFIG_PARAM_MEASUREMENT_TCPFLOW) == 0){
	    FlowAbstract* fa=new FlowAbstract();
	    fa->configTraceType(mConfigParam.getContextType());
	    mTrafficAbstract.push_back((int*)fa);
	}
}

void PacketAnalyzer::clearConfig(){
    mTraceList.clear();
    mTrafficAbstract.clear();
}

void PacketAnalyzer::setConfigParam(ConfigParam param){
    mConfigParam=param;
    config();
}

void PacketAnalyzer::setResult(Result* r) {
	finalResult = r;
}

Context& PacketAnalyzer::getContext(){
    return mTraceCtx;
}

ConfigParam PacketAnalyzer::getConfigParam(){
    return mConfigParam;
}

string PacketAnalyzer::getFolder(string s) {
	int pos = s.rfind("/");
	return s.substr(0, pos+1);
}

string PacketAnalyzer::getUserID(string s) {
	int pos1 = s.rfind("/");
	int pos2 = s.rfind("-");
	return s.substr(pos2 + 1, pos1-pos2-1);
}

void PacketAnalyzer::run() {
	// read packet
	char errbuf[PCAP_ERRBUF_SIZE];
	vector<string>::iterator it;
	pcap_t *trace_file;

	string curr_folder, tmp_folder, tmp_s;
	int trace_count = 0;
	int c_cycle = mConfigParam.getCountCycle();
	for (it = mTraceList.begin(); it != mTraceList.end(); it++) {
		if (trace_count % c_cycle == 0) {
			cout << trace_count << " files processed." << endl;
		}

		// open pcap file successfully?
		if ((trace_file = pcap_open_offline(it->c_str(), errbuf)) == NULL) {
			cout << " Unable to open the file: " << *it << endl;
			continue;
		}

		if (mConfigParam.isTraceType(CONFIG_PARAM_TRACE_DEV)) {
			// read application map, screen status and process stat
			//cout << "get user id" << endl;
			tmp_folder = getFolder(*it);
			tmp_folder += "appname";
			if (tmp_folder.compare(curr_folder) != 0) {
				curr_folder = tmp_folder;
				//cout << "Folder Name: " << curr_folder << endl;
				mTraceCtx.clearAppNameMap();

				ifstream appNameFile(tmp_folder.c_str());
				while (getline(appNameFile, tmp_s)) {
					mTraceCtx.addAppName(tmp_s);
				}

				mTraceCtx.updateFile(getFolder(*it));
			}

			// get user ID
			mTraceCtx.setUserID(getUserID(*it));
		}


		// pcap link layer header length

		if (pcap_datalink(trace_file) == DLT_LINUX_SLL) {
			mTraceCtx.setEtherLen(16);
		} else {
			mTraceCtx.setEtherLen(14);
			if (mConfigParam.isTraceType(CONFIG_PARAM_TRACE_DEV)) {
				trace_count++;
				cout << "Skip Wi-Fi trace: " << *it << endl;
				continue;
			}
		}

		//cout << "Pcap trace Ethernet header length: " << mTraceCtx.getEtherLen() << endl;

		/* read and dispatch packets until EOF is reached */
		pcap_loop(trace_file, 0, dispatcher_handler, (u_char *) this);
		pcap_close(trace_file);
		trace_count++;
	}

	//finalResult->closeAllResultFiles();
	vector<int*>::iterator end_it;
	for (end_it = mTrafficAbstract.begin(); end_it != mTrafficAbstract.end(); end_it++) {
		((TrafficAbstract*)(*end_it))->runCleanUp(finalResult);
	}

	// end
	finalResult->flush();
}

void PacketAnalyzer::runTrafficAbstract(Context& ctx, const struct pcap_pkthdr *header, const u_char *pkt_data) {
	vector<int*>::iterator it;
	for (it = mTrafficAbstract.begin(); it != mTrafficAbstract.end(); it++) {
		((TrafficAbstract*)(*it))->runMeasureTask(finalResult, ctx, header, pkt_data);
	}
}
