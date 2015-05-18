/*
 * tcp_flow.h
 *
 *  Created on: Dec 7, 2013
 *      Author: Junxian, Yihua
 */

#ifndef _PACO_TCP_FLOW_H
#define _PACO_TCP_FLOW_H

#include "common/basic.h"
#include "common/io.h"
#include "common/stl.h"
#include "proto/tcp_ip.h"
#include "proto/http.h"

class TCPFlow {
public:
    string flowIndex;
    u_int svr_ip;
    u_int clt_ip;
    u_short svr_port;
    u_short clt_port;
    double actual_ts;
    double gval;
    u_int u_int_start;
    double double_start;
    int promotion_delay;
    u_int window_scale;
    u_int window_initial_size;
    u_int window_size;
    double unaffected_time;

    double target;
    double bwstep;
    double last_time;
    double last_throughput;

    double start_time;
    double tmp_start_time;
    double first_byte_time; //first byte from server to client
    double last_byte_time; //last byte from server to client
    double last_payload_time; //last byte for both uplink and downlink
    double first_ul_pl_time, first_dl_pl_time, last_ul_pl_time, last_dl_pl_time;
    double last_dl_ack_time, last_ul_ack_time;

    int last_payload, last_payload_h;
    int last_pl_dir;

    int networkType;

    double dl_time, ul_time;

    double end_time;
    double idle_time;
    double syn_rtt, syn_ack_rtt;
    double idle_time_before_syn;

    double last_tcp_ts;

    short si; //circular seq index 0 - 19, point to the current last element
    short sx; // point to the current first index
    u_int seq_down[SEQ_INDEX_MAX]; //circular arrary, seq_down[si] is the last packet
    double seq_ts[SEQ_INDEX_MAX]; //corresponding time

    short ai; //circular ack index 0 - 9
    short ax; // point to the current first index
    u_int ack_down[ACK_INDEX_MAX]; //circular arrary
    double ack_ts[ACK_INDEX_MAX]; //corresponding time

    bool has_ts_option_clt;
    bool has_ts_option_svr;

    bool flow_finish;

    uint64 total_ul_payload, total_dl_payload;
    uint64 total_ul_whole, total_dl_whole;
    uint64 total_ul_payload_h, total_dl_payload_h;
    uint64 dl_rate_payload, ul_rate_payload, dl_rate_payload_h, ul_rate_payload_h;

    uint64 bytes_in_fly;
    uint64 max_bytes_in_fly;
    uint64 packet_count;
    uint64 app_packet_count;
    uint64 dup_ack_count;
    uint64 outorder_seq_count;
    double total_bw;
    int sample_count;

    double first_bw;
    u_short dup_ack_count_current;
    u_short slow_start_count; // start from 1 initial slow start
    double last_dupack_time;
    u_int bytes_after_dupack;

    bool start_compute_energy;
    double active_energy, passive_energy;
    double http_active_energy, http_passive_energy;
    double last_response_ts;
    //HTTP analysis
    u_short http_request_count;
    string first_content_type, first_user_agent, first_host; 
    string content_type;
    string user_agent;
    string host;
    string content_length;
    u_int total_content_length;
    string energy_log;
    string http_ts_log;
    string fgLog;
    
    double lastStatusTime;
    int lastStatus;

    string full_url;
    
    map<u_int, u_int> requestSeq;
    map<u_int, u_int>::iterator requestSeqIt;

    map<u_int, u_int> responseSeq;
    map<u_int, u_int>::iterator responseSeqIt;

    string userID;
    string appName;
    //called during init or any abnormal happens
    void reset_seq();
    void reset_ack();

    //functions for BW estimation - appear to be unused
    void update_seq(u_int seq, u_short payload_len, double ts);
    void update_ack(u_int ack, u_short payload_len, double ts, double _actual_ts);

    //functions for RTT analysis - appear to be unused
    void update_seq_x(u_int seq, u_short payload_len, double ts);
    void update_ack_x(u_int ack, u_short payload_len, double _actual_ts);

    //test with start_ai and ai
    bool bw_estimate(short start_ai);
    short find_seq_by_ack(u_int ack, short start, short end);
    short get_si_next(short c);
    short get_si_previous(short c);
    short get_ai_next(short c);
    short get_ai_previous(short c);
    void print(u_short processed_flags);
	TCPFlow();

	char * ConvertIPToString(unsigned int ip);
	void setUserID(string s);
};

#endif /* _PACO_TCP_FLOW_H */
