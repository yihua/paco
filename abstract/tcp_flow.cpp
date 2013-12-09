/*
 * tcp_flow.cpp
 *
 *  Created on: Dec 7, 2013
 *      Author: yihua
 */

#include "abstract/tcp_flow.h"

TCPFlow::TCPFlow() {
    svr_ip = 0;
    clt_ip = 0;
    svr_port = 0;
    clt_port = 0;
    start_time = 0;
    end_time = 0;
    idle_time = 0;

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

    total_down_payloads = 0;
    total_up_payloads = 0;
    bytes_in_fly = 0;
    max_bytes_in_fly = 0;
    packet_count = 0;
    dup_ack_count = 0;
    outorder_seq_count = 0;

    first_bw = 0;
    dup_ack_count_current = 0;
    slow_start_count = 1; // start from 1 initial slow start
    last_dupack_time = 0;
    bytes_after_dupack = 0;

    //HTTP analysis
    http_request_count = 0;
    content_type = "";
    user_agent = "";
    host = "";
    total_content_length = 0;

    total_bw = 0;
    sample_count = 0;

    reset_seq(); //contains reset_ack
}


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

//functions for RTT analysis
void TCPFlow::update_seq_x(u_int seq, u_short payload_len, double ts) {
    if (si != -1 && seq_down[si] > 0 && seq_down[si] > seq) {
        outorder_seq_count++;
        return;
    }
    si = get_si_next(si);
    seq_down[si] = seq + payload_len;
    seq_ts[si] = ts;
    if (sx == -1) {
        sx = si;
    } else if (sx == si) {
        sx = get_si_next(si);
    }

    if (payload_len > 0) {
        //Slow start after dup ack
        /*if (dup_ack_count_current > 20) {
            bytes_after_dupack += payload_len;
            if (first_bw == 0 && ts - last_dupack_time > DUPACK_SLOWSTART_TIME && ts - last_dupack_time <= 2 * DUPACK_SLOWSTART_TIME) {
                //this is the time to output a throughput sample
                double bw = bytes_after_dupack * 8 / (ts - last_dupack_time) / 1000.0; //kbps
                first_bw = bw;
                bytes_after_dupack = 0;

            } else if (first_bw > 0 && ts - last_dupack_time > 2 * DUPACK_SLOWSTART_TIME) {
                double bw = bytes_after_dupack * 8 / (ts - last_dupack_time - DUPACK_SLOWSTART_TIME) / 1000.0; //kbps
                if (first_bw > 0 && bw / first_bw > 1.5) {
                    slow_start_count++;
                }
                printf("SSBW %.4lf %.4lf %d\n", bw / first_bw, bw, dup_ack_count_current);
                dup_ack_count_current = 0;
                bytes_after_dupack = 0;
                first_bw = 0;
            }
        }//*/

        //Bytes in flight
        if (ai == -1) {
            bytes_in_fly = payload_len;
        } else {
            bytes_in_fly = seq_down[si] - ack_down[ai];
        }
        if (bytes_in_fly > max_bytes_in_fly) {
            max_bytes_in_fly = bytes_in_fly;
        }
    }

    if (bytes_in_fly == window_size || window_size == 0) {
        //window full or 0 window
        if (unaffected_time == 0) {
            unaffected_time = ts;
        }
    }


    if (last_time < 0) {
        last_time = ts;
    }

    if (payload_len > 0 && ts - last_time > IDLE_THRESHOLD) {
        idle_time += (ts - last_time);
        //printf("I %.4lf D\n", ts - last_time);
    }

    if (packet_count == 2) {
        syn_rtt = ts - last_time;
    } else if (packet_count == 3) {
        syn_ack_rtt = ts - last_time;
    }
    last_time = ts;
}

void TCPFlow::update_ack_x(u_int ack, u_short payload_len, double _actual_ts) {
    if (ai != -1 && ack_down[ai] > 0 && ack_down[ai] == ack && payload_len == 0) {
        //if payload not 0, this is uplink data packet
        dup_ack_count++;
        if (_actual_ts - last_dupack_time > 1.0) {
            //new session
            dup_ack_count_current = 1;
        } else {
            dup_ack_count_current++;
        }
        last_dupack_time = _actual_ts;
        bytes_after_dupack = 0;
        return;
    }

    ai = get_ai_next(ai);
    ack_down[ai] = ack;
    ack_ts[ai] = _actual_ts;
    if (ax == -1) {
        ax = ai;
    } else if (ax == ai) {
        ax = get_ai_next(ai);
    }

    /*//ACK RTT analysis
    short s1 = find_seq_by_ack(ack_down[ai], sx, si);
    if (s1 != -1 && payload_len == 0) {
        cout << "AR " << " " << ack_ts[ai] - seq_ts[s1] << " " << bytes_in_fly << endl;
    }//*/

    //update bytes in fly after analysis
    if (bytes_in_fly > 0) {
        bytes_in_fly = seq_down[si] - ack_down[ai];
    }

    if (last_time < 0) {
        last_time = _actual_ts;
    }
    if (payload_len > 0 && _actual_ts - last_time > IDLE_THRESHOLD) {
        idle_time += (_actual_ts - last_time);
        //printf("I %.4lf U\n", _actual_ts - last_time);
    }

    if (packet_count == 2) {
        syn_rtt = _actual_ts - last_time;
    } else if (packet_count == 3) {
        syn_ack_rtt = _actual_ts - last_time;
    }
    last_time = _actual_ts;
}

//test with start_ai and ai
bool TCPFlow::bw_estimate(short start_ai) {
    if (ack_down[start_ai] - ack_down[get_ai_previous(start_ai)] <= 1.1 * TCP_MAX_PAYLOAD) {
        return false; //this ack is triggered by TCP's delayed ACK
    }

    if (ack_down[ai] - ack_down[get_ai_previous(ai)] <= 1.1 * TCP_MAX_PAYLOAD) {
        return false; //this ack is triggered by TCP's delayed ACK
    }


    short s1 = find_seq_by_ack(ack_down[start_ai], sx, si);
    short s2 = find_seq_by_ack(ack_down[ai], sx, si);
    if (s1 == -1 || s2 == -1 || s1 == s2)
        return false;

    if ((seq_ts[s2] - seq_ts[s1] == 0) ||
        (seq_ts[s2] - seq_ts[s1] > 0)) {
        double bw = (double)(seq_down[s2] - seq_down[s1]) * 8.0 / (ack_ts[ai] - ack_ts[start_ai]) / ONE_MILLION;
        double bw_send;
        if (seq_ts[s2] - seq_ts[s1] == 0) {
            bw_send = BW_MAX_BITS_PER_SECOND * 2.0 / ONE_MILLION;
        } else {
            bw_send = (double)(seq_down[s2] - seq_down[s1]) * 8.0 / (seq_ts[s2] - seq_ts[s1]) / ONE_MILLION;
        }

        if (bw < 45000000.0 / ONE_MILLION  &&
            bw_send >= BW_MAX_BITS_PER_SECOND / ONE_MILLION) {

            if (actual_ts - last_time > bwstep) {
                //cout << bw_send << " " << hex << ack_down[start_ai] << " " << ack_down[ai] << dec << endl;
                cout << "BWES " << ConvertIPToString(clt_ip) << " " << actual_ts << " " << bw << " " << ack_ts[ai] - ack_ts[start_ai] << endl;
                total_bw += bw;
                sample_count++;
            }

            /*
             //time sample for each step
             string big_flow_index = ConvertIPToString(clt_ip) + string("_");
            big_flow_index += ConvertIPToString(svr_ip) + string("_");
            big_flow_index += NumberToString(clt_port) + string("_") + NumberToString(svr_port);

            while (actual_ts > target + 0.4 * bwstep) {
                if (abs(last_time - target) <= 0.4 * bwstep) {
                    //cout << "BW_ESTIMATE_SAMPLE " << big_flow_index << " " << target << " " << last_throughput << " " << abs(ack_ts[ai] - ack_ts[start_ai]) << " " << (seq_down[s2] - seq_down[s1]) << endl;
                    total_bw += last_throughput;
                    sample_count++;
                } else {
                    //cout << "BW_ESTIMATE_SAMPLE " << target << " " << 0 << " " << 0 << endl;
                }
                target += bwstep;
            }
            //actual_ts <= target + 0.2 * bwstep
            if (last_time <= target && target <= actual_ts) {
                if (abs(last_time - target) < abs(actual_ts - target)) {
                    //cout << "BW_ESTIMATE_SAMPLE " << big_flow_index << " " << target << " " << last_throughput << " " << (ack_ts[ai] - ack_ts[start_ai]) << " " << (seq_down[s2] - seq_down[s1]) << endl;
                    total_bw += last_throughput;
                    sample_count++;
                } else {
                    //cout << "BW_ESTIMATE_SAMPLE " << big_flow_index << " " << target << " " << bw << " " << (ack_ts[ai] - ack_ts[start_ai]) << " " << (seq_down[s2] - seq_down[s1]) << endl;
                    total_bw += bw;
                    sample_count++;
                }
                target += bwstep;
            } else if (target < last_time) {
                if (abs(last_time - target) <= 0.4 * bwstep) {
                    //cout << "BW_ESTIMATE_SAMPLE " << big_flow_index << " " << target << " " << last_throughput << " " << (ack_ts[ai] - ack_ts[start_ai]) << " " << (seq_down[s2] - seq_down[s1]) << endl;
                    total_bw += last_throughput;
                    sample_count++;
                } else {
                    //cout << "BW_ESTIMATE_SAMPLE " << target << " " << 0 << " " << 0 << endl;
                }
                target += bwstep; //should have already output when scanning last_time
            } else if (target > actual_ts) {

            //} else {//impossible to reach here
            }//*/

            /*cout << "BW_ESTIMATE " << ConvertIPToString(svr_ip);
            cout << " => " << ConvertIPToString(clt_ip);
            cout.precision(6);
            cout << " time " << fixed << actual_ts;
            cout << " BW " << bw << " Mbps";
            //cout << " start " << hex << ack_down[start_ai] << " end " << ack_down[ai] << dec;
            cout << " ACK_GAP " << ack_down[ai] - ack_down[start_ai];
            cout << " ACK_TIME_GAP " << ack_ts[ai] - ack_ts[start_ai];
            cout << endl;//*/

            last_time = actual_ts;
            last_throughput = bw;
            return true;
        }
    }

    return false;
}

short TCPFlow::find_seq_by_ack(u_int ack, short start, short end) {
    int range;
    if (start <= end) {
        range = end - start + 1;
    } else {
        range = end + SEQ_INDEX_MAX - start + 1;
    }

    if (range <= 8) {
        for (int i = start ; i <= end ; i++) {
            if (seq_down[i] == ack)
                return i;
        }
    } else {
        int mid = (start + range / 2) % SEQ_INDEX_MAX;
        if (ack == seq_down[mid]) {
            //bingo!
            return mid;
        } else if (ack > seq_down[mid]) {
            //second half
            return find_seq_by_ack(ack, get_si_next(mid), end);
        } else {
            return find_seq_by_ack(ack, start, get_si_previous(mid));
        }
    }
    return -1;
}

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
           total_down_payloads, //12
           total_up_payloads, //13
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
	            ip & 0xFF,
	            (ip >> 8) & 0xFF,
	            (ip >> 16) & 0xFF,
	            ip >> 24);
	        return ipstr;
	}
