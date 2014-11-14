/*
 * flow_abstract.h
 *
 *  Created on: Dec 8, 2013
 *      Author: yihua
 */

#ifndef FLOW_ABSTRACT_H_
#define FLOW_ABSTRACT_H_

#include "framework/traffic_abstract.h"
#include "framework/pcap.h"
#include "proto/tcp_ip.h"
#include "proto/gtp.h" 
#include "proto/http.h"
#include "proto/8021q.h"
#include "abstract/tcp_flow.h"
#include "common/basic.h"
#include "common/stl.h"
#include "common/output.h"
#include "framework/user.h"
#include "framework/context.h"
#include "param/config_param.h"

#define HTTP_THRESHOLD 1

#define CC_SAMPLE_PERIOD 10.0 // s

#define MAX_PKT_INTERARRIVAL 1.0 // s

//Usage: StringToNumber<Type> (String);
template <typename T>
T StringToNumber (const string &Text) {
    istringstream ss(Text);
    T result;
    return ss >> result ? result : 0;
}

class FlowAbstract: public TrafficAbstract{
	int BURST_THRESHOLD;
	double TIME_BASE;

	uint64 packet_count;
	uint64 no_ip_count;
	uint64 tcp_count;
	uint64 udp_count;
	uint64 tcp_up_bytes;
	uint64 tcp_down_bytes;
	uint64 udp_up_bytes;
	uint64 udp_down_bytes;
	uint64 http_up_bytes;
	uint64 http_down_bytes;
	uint64 icmp_count;
	uint64 ignore_count1;
	uint64 ignore_count2;
	uint64 flow_count;
	ip *ip_hdr;
	tcphdr *tcp_hdr;
	udphdr *udp_hdr;
	gtphdr *gtp_hdr;
	bool b1, b2;
	bool is_first;
	uint64 start_time_sec;
	uint64 last_time_sec;
	uint64 end_time_sec;
	u_int ip1, ip2;
	u_int ip_clt, ip_svr;
	u_short port_clt, port_svr;

	u_short ip_whole_len, ip_payload_len;
	u_short payload_len, tcp_whole_len;

	double ts;
	double last_prune_time;
	double last_sample_time;
	double ack_delay;
	u_int expected_ack;
	u_int *opt_ts;
	u_short opt_len;
	u_int window_scale;

	__gnu_cxx::hash_set<u_int> enb_ip;
	__gnu_cxx::hash_set<u_int> core_ip;
	__gnu_cxx::hash_map<u_int, u_int> enb_load;
	__gnu_cxx::hash_map<u_int, u_int>::iterator itmap;

	//map<string, TCPFlow>::iterator flow_it;
	//map<string, TCPFlow>::iterator flow_it_tmp;
	//map<string, TCPFlow> client_flows;
	map<string, pair<double, double> > big_flows;
	map<string, pair<double, double> >::iterator big_flow_it_tmp;

	map<string, User> users;
	map<string, User>::iterator user_it;
	map<string, TCPFlow*>::iterator flow_it;
	map<string, TCPFlow*>::iterator flow_it_tmp;

	map<u_int, u_int> cip;
	map<u_int, u_int> sip;
	map<u_int, u_int>::iterator csit;

	string flow_index;
	string big_flow_index;

	bool is_target_flow;
	TCPFlow *flow;
	User *userp;
	//client_bw *bw_udp = NULL;
	//client_bw *bw_tcp = NULL;
	char *payload;
	string payload_str;
	size_t start_pos;
	size_t end_pos;
	u_int jump;

	bool isClient(in_addr addr);
	bool isControlledServer(in_addr addr);
	void printAddr(in_addr addr1, in_addr addr2);
	void writeTCPFlowStat(Result* result, const TCPFlow* tcpflow);
	void writeSessionStat(Result* result, const User* user);
	void writeRateStat(Result* result, const User* user);
	string traceType;

	int ETHER_HDR_LEN;

public:
	FlowAbstract();

	void bswapIP(struct ip* ip);
	void bswapTCP(struct tcphdr* tcphdr);
	void bswapUDP(struct udphdr* udphdr);
	void bswapGTP(gtphdr* gtphdr);
	//void bswapDNS(struct DNS_HEADER* dnshdr);

    string intToString(int x);

	void configTraceType(string type);
	string getTraceType();
	void runMeasureTask(Result* result, Context& traceCtx, const struct pcap_pkthdr *header, const u_char *pkt_data);
	void runCleanUp(Result* result);
};

#endif /* FLOW_ABSTRACT_H_ */
