/*
 * framework/packet_analyzer.h
 * PACO
 *
 * Created by: Yihua Guo, 12/05/2013
 *
 */

#ifndef _PACO_PACKET_ANALYZER_H
#define _PACO_PACKET_ANALYZER_H

#include "common/stl.h"
#include "framework/measure_task.h"
#include "framework/traffic_abstract.h"
#include "param/config_param.h"
#include "framework/pcap.h"
#include "common/basic.h"
#include "common/io.h"
#include "proto/tcp_ip.h"

class PacketAnalyzer {
private:
	vector<TrafficAbstract> mTrafficAbstract;
	vector<string> traceList;
	vector<string> appNameMap;

	int ETHER_HDR_LEN;
	string getFolder(string s);

public:
	PacketAnalyzer();

	void checkSystem();
	void config(ConfigParam param);
	int getEtherLen();
	void run();
	void runTrafficAbstract(int i, const struct pcap_pkthdr *header, const u_char *pkt_data);
};


#endif /* _PACO_PACKET_ANALYZER_H */
