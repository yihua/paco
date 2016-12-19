void TCPFlow::update_seq_x(u_int seq, u_short payload_len, double ts) {
    // only consider data packet
    if (payload_len == 0) {
        return;
    }
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
        printf("---- @@@ Seq array not large enough.");
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

    //ACK RTT analysis
    short s1 = find_seq_by_ack(ack_down[ai], sx, si);
    if (s1 != -1 && payload_len == 0) {
        //cout << "AR " << " " << ack_ts[ai] - seq_ts[s1] << " " << bytes_in_fly << endl;
    }//

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
