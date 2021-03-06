/*
 * tcp_flow.cpp
 *
 *  Created on: Dec 7, 2013
 *      Author: yihua
 */

#include "abstract/tcp_flow.h"

#define START_SEQ_WINDOW 40

TCPFlow::TCPFlow() {
    svr_ip = 0;
    clt_ip = 0;
    svr_port = 0;
    clt_port = 0;
    start_time = 0;
    end_time = 0;
    idle_time = 0;
    flag_order = 0;

    target = start_time + GVAL_TIME;
    bwstep = 0.25;
    last_time = -1;
    last_throughput = -1;

    syn_rtt = 0;
    syn_ack_rtt = 0;
    idle_time_before_syn = 0;

    gval = -1.0;
    u_int_start = 0;
    double_start = -1.0;
    promotion_delay = 0;
    window_scale = 0;
    window_initial_size = 0;
    window_size = 0;
    unaffected_time = 0;

    has_ts_option_clt = false;
    has_ts_option_svr = false;
    first_byte_time = 0;
    last_byte_time = 0;

    last_payload_time = -1.0;
    first_ul_pl_time = -1.0;
    first_dl_pl_time = -1.0;
    last_ul_pl_time = -1.0;
    last_dl_pl_time = -1.0;
    last_ul_ack_time = -1.0;
    last_dl_ack_time = -1.0;


    total_dl_payload = 0;
    total_ul_payload = 0;
    total_dl_payload_h = 0;
    total_ul_payload_h = 0;
    total_ul_whole = 0;
    total_dl_whole = 0;
    bytes_in_fly = 0;
    max_bytes_in_fly = 0;
    packet_count = 0;
    app_packet_count = 0;
    dup_ack_count = 0;
    outorder_seq_count = 0;

    first_bw = 0;
    dup_ack_count_current = 0;
    slow_start_count = 1; // start from 1 initial slow start
    last_dupack_time = 0;
    bytes_after_dupack = 0;

    start_compute_energy = false;
    active_energy = 0.0;
    passive_energy = 0.0;
    http_active_energy = 0.0;
    http_passive_energy = 0.0;
    last_response_ts = 0.0;
    
    networkType = -1;
    //HTTP analysis
    http_request_count = 0;
    content_type = "";
    user_agent = "";
    appName = "";
    host = "";
    first_content_type = "";
    first_user_agent = "";
    first_host = "";
    content_length = "";
    total_content_length = 0;
    energy_log = "";
    http_ts_log = "";
    fgLog = "";
    lastStatusTime = -1;
    lastStatus = -1;

    full_url = "|";

    total_bw = 0;
    sample_count = 0;

    last_pl_dir = -1;
    dl_time = 0.0;
    ul_time = 0.0;
    last_payload = 0;
    last_payload_h = 0;
    dl_rate_payload = 0;
    ul_rate_payload = 0; 
    dl_rate_payload_h = 0;
    ul_rate_payload_h = 0;
    flow_finish = false;
    //reset_seq_new(); //contains reset_ack
    si_down = -1;
    sx_down = -1;
    si_up = -1;
    sx_up = -1;
    down_rtt_size = START_SEQ_WINDOW;
    up_rtt_size = START_SEQ_WINDOW;

    seq_down = new u_int[down_rtt_size];
    seq_ack_down = new u_int[down_rtt_size];
    seq_down_ts = new double[down_rtt_size];

    seq_up = new u_int[up_rtt_size];
    seq_ack_up = new u_int[up_rtt_size];
    seq_up_ts = new double[up_rtt_size];
    //memset(seq_down, 0, sizeof seq_down);
    //memset(seq_ack_down, 0, sizeof seq_ack_down);
    //memset(seq_down_ts, 0, sizeof seq_down_ts);
    //memset(seq_up, 0, sizeof seq_up);
    //memset(seq_ack_up, 0, sizeof seq_ack_up);
    //memset(seq_up_ts, 0, sizeof seq_up_ts);

    minrtt_down = 1000000.0;
    minrtt_up = 1000000.0;
    avgrtt_down = 0.0;
    avgrtt_up = 0.0;
    down_count = 0;
    up_count = 0;

    all_avgrtt_down = 0.0;
    all_avgrtt_up = 0.0;
    all_down_count = 0;
    all_up_count = 0;
}

void TCPFlow::deleteArray() {
    delete[] seq_down;
    delete[] seq_ack_down;
    delete[] seq_down_ts;
    delete[] seq_up;
    delete[] seq_ack_up;
    delete[] seq_up_ts;
}

//TCPFlow::~TCPFlow() {
//	delete userID;
//}

/*
//called during init or any abnormal happens
void TCPFlow::reset_seq() {
    si = -1;
    sx = -1;
    memset(seq_down, 0, sizeof seq_down);
    memset(seq_ts, 0, sizeof seq_ts);

    reset_ack();
    //reset ack does not need to reset seq, since seq is ahead of ack
    //but reset seq needs to reset ack, since the existing acks are old
}

//called during init or any abnormal happens
void TCPFlow::reset_ack() {
    ai = -1;
    ax = -1;
    memset(ack_down, 0, sizeof ack_down);
    memset(ack_ts, 0, sizeof ack_ts);
}


//before this function is called, need to make sure that payload_len >= 1358 (should be == 1358 actually)
void TCPFlow::update_seq(u_int seq, u_short payload_len, double ts) {
    if (si != -1 && seq_down[si] > 0 && seq_down[si] > seq) {
        //out of order seq, ideally seq_down[si] == seq
        reset_seq();
        return;
    }

    if (si != -1 && ts >= seq_ts[si] + IDLE_THRESHOLD) {
        //there is long idle time between this packet and previous packet
        reset_seq();
        return;
    }

    if (payload_len == 0) {
        //does not consider 0-payload data packets, since it's ACK packets for uplink data
        reset_seq();
        return;
    }

    //!!!!!! seq here stores the next seq to send, so the corresponding ACK packet's ack is equal to this seq
    si = get_si_next(si);
    seq_down[si] = seq + payload_len;
    seq_ts[si] = ts;
    if (sx == -1) {
        sx = si;
    } else if (sx == si) {
        sx = get_si_next(si);
    }
}

void TCPFlow::update_ack(u_int ack, u_short payload_len, double ts, double _actual_ts) {
    if (ai != -1 && ack_down[ai] > 0 && ack_down[ai] >= ack) {
        //out of order ack, or dup ack, ideally ack_down[ai] < ack
        reset_ack();
        return;
    }

    if (ai != -1 && ts >= ack_ts[ai] + IDLE_THRESHOLD) {
        //there is long idle time between this packet and previous packet
        reset_ack();
        return;
    }

    if (payload_len > 0) {
        //we only consider 0-payload ACK packets, so that uplink data packets are not considered
        reset_ack();
        return;
    }

    actual_ts = _actual_ts;
    ai = get_ai_next(ai);
    ack_down[ai] = ack;
    ack_ts[ai] = ts;
    if (ax == -1) {
        ax = ai;
    } else if (ax == ai) {
        ax = get_ai_next(ai);
    }

    //check if existing bw sample exists
    if (gval <= 0.00001) {
        //no need to check for invalid gval
        return;
    }

    int m = get_ai_next(ax); //start from the second packet, so we can check the gap with the first ack
    //at least with two full packet samples
    while (m != ai && ack_down[m] != 0 && ack_ts[ai] - ack_ts[m] >= 20 * gval) { // 1/20 = 5% error
        if (bw_estimate(m)) {
            //reset after one successful bandwidth estimation  ? ? ?
            //reset_seq();
            break;
        }
        m = get_ai_next(m);
    }
}
*/
// ******************************************************************************************
//functions for RTT analysis
//Download analysis

void TCPFlow::update_seq_download(u_int seq, u_int ack, u_short payload_len, double ts) {
    update_seq_new(seq, ack, seq_down, seq_ack_down, seq_down_ts, down_rtt_size, si_down, sx_down, payload_len, ts);
}

void TCPFlow::update_seq_upload(u_int seq, u_int ack, u_short payload_len, double ts) {
    update_seq_new(seq, ack, seq_up, seq_ack_up, seq_up_ts, up_rtt_size, si_up, sx_up, payload_len, ts);
}

double TCPFlow::update_ack_download(u_int seq, u_int ack, u_short payload_len,
    double ts, Result* result) {
	//return -1;
    return update_ack_new(seq, ack, seq_down, seq_ack_down, seq_down_ts, down_rtt_size, si_down, sx_down, payload_len, ts, result, 1);
}

double TCPFlow::update_ack_upload(u_int seq, u_int ack, u_short payload_len,
    double ts, Result* result) {
	//return -1;
    return update_ack_new(seq, ack, seq_up, seq_ack_up, seq_up_ts, up_rtt_size, si_up, sx_up, payload_len, ts, result, 0);
}

void TCPFlow::update_seq_new(u_int seq, u_int ack, u_int * & seq_array, u_int * & ack_array,
    double * & seq_ts, int & seq_size, int & si, int & sx, u_short payload_len, double ts) {
    // only consider data packet
    if (payload_len == 0) {
        return;
    }
    if (packet_count <= 3) {
    	return;
    }
    if (si != -1 && seq_array[si] > 0 && seq_array[si] > seq) {
        //outorder_seq_count++;
        return;
    }
    if (ts == 0) {
        printf("Timestamp Error");
    }
    //printf("start\n");
    si = get_si_next_new(si, seq_size);
    if (sx == -1) {
        sx = si;
    } else if (sx == si) {
        //printf("---- @@@ Seq array not large enough. seq_size=%d\n", seq_size); 
	
        u_int * old_seq = seq_array;
        u_int * old_ack = ack_array;
        double * old_ts = seq_ts;

		int end = (sx + seq_size - 1) % seq_size;
        int old_size = seq_size;
		
		seq_size *= 2;
		seq_array = new u_int[seq_size];
        ack_array = new u_int[seq_size];
		seq_ts = new double[seq_size];
		
		int index = 0, i = sx;
        
		while (i != end) {
            seq_array[index] = old_seq[i];
            ack_array[index] = old_ack[i];
            seq_ts[index] = old_ts[i];
            index += 1;
            i = get_si_next_new(i, old_size);
		}
		seq_array[index] = old_seq[i];
        ack_array[index] = old_ack[i];
        seq_ts[index] = old_ts[i];
        //index += 1;
		
		sx = 0;
        si = index + 1;

		
		if (index != old_size - 1) {
			printf("Copy error: index=%d, oldsize=%d\n", index, old_size);
		}
        delete[] old_seq;
        delete[] old_ack;
        delete[] old_ts;
		
        //sx = get_si_next_new(si, seq_size);
	
    }
    seq_array[si] = seq + payload_len;
    ack_array[si] = ack;
    seq_ts[si] = ts;
    //printf("end\n");
}

double TCPFlow::update_ack_new(u_int seq, u_int ack, u_int * seq_array, u_int * ack_array,
    double * seq_ts, int & seq_size, int & si, int & sx, u_short payload_len, double _actual_ts, Result* result, int flag) {

    if (payload_len > 0) {
        return -1;
    }

    if (packet_count <= 3) {
    	return -1;
    }

    //ACK RTT analysis
    //printf("start=%d end=%d ", sx, si);
    int s1 = find_seq_by_ack_new(seq, ack, sx, si, seq_array, ack_array, seq_size);
    //printf("index=%d seq_ts=%.6lf\n", s1, seq_ts[s1]);
    if (s1 >= 0) {
        char buf[1000];
        sprintf(buf, "%s %d.%d.%d.%d:%d %d.%d.%d.%d:%d %d %.6lf %.6lf %.6lf %s\n",
            this->userID.c_str(), 
            (this->clt_ip)>>24, (this->clt_ip)>>16 & 0xFF, (this->clt_ip)>>8 & 0xFF, (this->clt_ip) & 0xFF,
            this->clt_port,
            (this->svr_ip)>>24, (this->svr_ip)>>16 & 0xFF, (this->svr_ip)>>8 & 0xFF, (this->svr_ip) & 0xFF,
            this->svr_port,
            flag,
            seq_ts[s1], _actual_ts, _actual_ts - seq_ts[s1],
            this->appName.c_str());
        result->addResultToFile(7, buf);
        return _actual_ts - seq_ts[s1];
    }
    return -1.0;
}

int TCPFlow::get_si_next_new(int c, int size) {
    return (c + 1) % size;
}

int TCPFlow::find_seq_by_ack_new(u_int seq, u_int ack, int & start, int & end,
    u_int * seq_array, u_int * ack_array, int & seq_size) {
    if (start == -1 && end == -1) {
        return -1;
    } else {
        if (start == -1 || end == -1) {
            printf("------ ### RTT array error!");
        }
    }
    int i = start, last = get_si_next_new(end, seq_size);
    int guard = 0, test = 0;
    if (start == last) test = 1;
    while (1) {
        if (test > 0) {
            if (i == last && guard == 1) {
                break;
            }
            if (i == last && guard == 0) {
                guard = 1;
            }
        } else {
	    if (i == last) break;
        }
        if (ack > seq_array[i]) {
            start = get_si_next_new(start, seq_size);
        } else if (ack == seq_array[i]) {
            if (seq == ack_array[i]) {
                if (start == end) {
                    start = -1;
                    end = -1;
                } else {
                    start = get_si_next_new(start, seq_size);
                }
                return i;
            }

            if (start == end) {
                start = -1;
                end = -1;
            } else {
                start = get_si_next_new(start, seq_size);
            }
            return -1;
        } else {
            return -1;
        }
        i = get_si_next_new(i, seq_size);
        if (start != i) {
            printf("### ERROR in RTT analysis");
        }
    }

    start = -1;
    end = -1;
    return -1;
}

/*
short TCPFlow::get_si_next(short c) {
    return (c + 1) % SEQ_INDEX_MAX;
}

short TCPFlow::get_si_previous(short c) {
    return (c - 1 + SEQ_INDEX_MAX) % SEQ_INDEX_MAX;
}

short TCPFlow::get_ai_next(short c) {
    return (c + 1) % ACK_INDEX_MAX;
}

short TCPFlow::get_ai_previous(short c) {
    return (c - 1 + ACK_INDEX_MAX) % ACK_INDEX_MAX;
}
*/

void TCPFlow::print(u_short processed_flags) {
    double avg_bw = 0;
    if (sample_count > 0)
        avg_bw = (double)(total_bw / (double)sample_count);
    if (user_agent.length() == 0)
        user_agent = "!";
    if (content_type.length() == 0)
        content_type = "!";
    if (host.length() == 0)
        host = "!";


    printf("%s ", ConvertIPToString(clt_ip)); // 1
    printf("%s ", ConvertIPToString(svr_ip)); //2


    printf("%d %d %.4lf %.4lf %.4lf %.4lf %d %d %d %lld %lld %.4lf %lld %.4lf %.4lf %lld %lld %.4lf %d %.4lf %d %lld %.4lf %.4lf %d %d %d %.4lf ",
           clt_port, //3
           svr_port, //4
           start_time, //5
           first_byte_time - start_time, //6
           last_byte_time - start_time, //7
           end_time - start_time, //8
           processed_flags, //9
           has_ts_option_clt, //10
           has_ts_option_svr, //11
           total_dl_payload, //12
           total_ul_payload, //13
           idle_time, //14
           max_bytes_in_fly, //15
           syn_rtt, //16
           syn_ack_rtt, //17
           dup_ack_count, //18
           outorder_seq_count, //19
           avg_bw, //20
           sample_count, //21
           gval, //22
           slow_start_count, //23
           packet_count, //24
           promotion_delay * gval - (syn_rtt + syn_ack_rtt), //25
           idle_time_before_syn, //26
           http_request_count, //27
           window_scale, //28
           window_initial_size, //29
           unaffected_time //30
           );
    printf("%s %s %s %d\n",
           user_agent.c_str(), //31
           content_type.c_str(), //32
           host.c_str(), //33
           total_content_length //34
           );
}


char* TCPFlow::ConvertIPToString(unsigned int ip) {
        static char ipstr[17];
        sprintf(ipstr, "%d.%d.%d.%d",
            ip >> 24,
            (ip >> 16) & 0xFF,
            (ip >> 8) & 0xFF,
            ip & 0xFF);
        return ipstr;
}

void TCPFlow::setUserID(string s) {
	this->userID = s;
}
