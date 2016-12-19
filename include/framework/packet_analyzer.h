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
#include "framework/context.h"
#include "framework/result.h"
#include "param/config_param.h"
#include "framework/pcap.h"
#include "common/basic.h"
#include "common/io.h"
#include "proto/tcp_ip.h"

class PacketAnalyzer {
private:

    // Actually a list of pointers to flowAbstract objects?
	vector<int*> mTrafficAbstract;

    // List of filenames of trace files
	vector<string> mTraceList;

	Context mTraceCtx;
	ConfigParam mConfigParam;
	Result* finalResult;

	string getFolder(string s);
	string getUserID(string s);

public:
	PacketAnalyzer();

    /* Print endianness, size of uint64 but doesn't seem to configure 
     * anything
     */
	void checkSystem();

    /* 
     * 1. Fetch items in the trace list
     * 2. If TCP, load FlowAbstract and add to the mTrafficAbstract list.
     * Other types not yet supported
     */
	void config();

    /*
     * Clear mTrafficAbstract and mTraceList
     */
	void clearConfig();

    /*
     * Set mConfigParam
     * Run config() (i.e. load trace and FlowAbstract objects)
     */
	void setConfigParam(ConfigParam param);

    /*
     * Set up class for saving results to a file
     */
	void setResult(Result* r);

	Context& getContext();
	ConfigParam getConfigParam();

    /*
     * Iterate through all trace files, open them
     * Parse the app name files and add them to the context
     * Then process all pcap traces
     */
	void run(char* filterID);

    /*
     * called by run() on each packet, this gathers data from the packets.
     */
	void runTrafficAbstract(Context& traceCtx, const struct pcap_pkthdr *header, const u_char *pkt_data);
};


#endif /* _PACO_PACKET_ANALYZER_H */
