/*
 * framework/packet_analyzer.cpp
 * PACO
 *
 * Created by: Yihua Guo, 12/05/2013
 *
 */

#include "common/basic.h"
#include "common/io.h"
#include "framework/packet_analyzer.h"
#include "framework/pcap.h"

void dispatcher_handler(u_char *c, const struct pcap_pkthdr *header, const u_char *pkt_data) {

}

PacketAnalyzer::PacketAnalyzer() {
	ETHER_HDR_LEN = 0;
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

void PacketAnalyzer::run() {
	// read packet
	char errbuf[PCAP_ERRBUF_SIZE];
	vector<string>::iterator it;
	pcap_t *trace_file;

	for (it = traceList.begin(); it != traceList.end(); it++) {
		// open pcap file successfully?
		if ((trace_file = pcap_open_offline(it->c_str(), errbuf)) == NULL) {
			cout << stderr << " Unable to open the file %s\n" << *it << endl;
			continue;
		}

		// pcap link layer header length

		if (pcap_datalink(trace_file) == DLT_LINUX_SLL) {
			ETHER_HDR_LEN = 16;
		} else {
			ETHER_HDR_LEN = 14;
		}

		cout << "Pcap trace Ethernet header length: " << ETHER_HDR_LEN << endl;

		/* read and dispatch packets until EOF is reached */
		pcap_loop(trace_file, 0, dispatcher_handler, NULL);
		pcap_close(trace_file);
	}
}
