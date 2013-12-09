/*
 * framework/packet_analyzer.cpp
 * PACO
 *
 * Created by: Yihua Guo, 12/05/2013
 *
 */

#include "framework/packet_analyzer.h"

void dispatcher_handler(u_char *c, const struct pcap_pkthdr *header, const u_char *pkt_data) {
	PacketAnalyzer* analyzer = (PacketAnalyzer *) c;
	analyzer->runTrafficAbstract(analyzer->getEtherLen(), header, pkt_data);
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

void PacketAnalyzer::config(ConfigParam param) {
	ifstream trace_list(param.getTraceList().c_str());
	string s;
	while (getline(trace_list, s)) {
		traceList.push_back(s);
	}
}

int PacketAnalyzer::getEtherLen() {
	return ETHER_HDR_LEN;
}

string PacketAnalyzer::getFolder(string s) {
	int pos = s.rfind("/");
	return s.substr(0, pos+1);
}

void PacketAnalyzer::run() {
	// read packet
	char errbuf[PCAP_ERRBUF_SIZE];
	vector<string>::iterator it;
	pcap_t *trace_file;

	string curr_folder, tmp_folder, tmp_s;
	int trace_count = 0;
	for (it = traceList.begin(); it != traceList.end(); it++) {
		if (trace_count % 1000 == 0) {
			cout << trace_count << " files processed." << endl;
		}

		// open pcap file successfully?
		if ((trace_file = pcap_open_offline(it->c_str(), errbuf)) == NULL) {
			cout << " Unable to open the file: " << *it << endl;
			//continue;
		}

		// read application map
		tmp_folder = getFolder(*it);
		tmp_folder += "appname";
		if (tmp_folder.compare(curr_folder) != 0) {
			curr_folder = tmp_folder;
			cout << "Folder Name: " << curr_folder << endl;
			appNameMap.clear();

			ifstream appNameFile(tmp_folder.c_str());
			while (getline(appNameFile, tmp_s)) {
				appNameMap.push_back(tmp_s);
			}
		}

		// pcap link layer header length

		if (pcap_datalink(trace_file) == DLT_LINUX_SLL) {
			ETHER_HDR_LEN = 16;
		} else {
			ETHER_HDR_LEN = 14;
		}

		cout << "Pcap trace Ethernet header length: " << ETHER_HDR_LEN << endl;

		/* read and dispatch packets until EOF is reached */
		pcap_loop(trace_file, 0, dispatcher_handler, (u_char *) this);
		pcap_close(trace_file);
		trace_count++;
	}
}

void PacketAnalyzer::runTrafficAbstract(int i, const struct pcap_pkthdr *header, const u_char *pkt_data) {
	vector<TrafficAbstract>::iterator it;

	for (it = mTrafficAbstract.begin(); it != mTrafficAbstract.end(); it++) {
		it->runMeasureTask(header, pkt_data);
	}
}
