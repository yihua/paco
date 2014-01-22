/*
 * flow_abstract.cpp
 *
 *  Created on: Dec 8, 2013
 *      Author: yihua
 */

#include "abstract/flow_abstract.h"

FlowAbstract::FlowAbstract() {
	is_first = true;
	BURST_THRESHOLD = 1;
	cout << "BURST_THRESHOLD: " << BURST_THRESHOLD << " s" << endl;
	TIME_BASE = 1350014400.000000; //Thu Oct 12 2012 00:00:00
	traceType = "0";
	flow=NULL;
	userp=NULL;
}

void FlowAbstract::configTraceType(string type) {
	traceType = type;
}

bool FlowAbstract::isClient(in_addr addr) {
        //for Yihua's trace, server trace: client is 198.*; client trace: client is 10.*; and 32.* for 3G trace
        return (((addr.s_addr & 0xFF) == 192 && (addr.s_addr & 0xFF00) >> 8 == 168) ||
        		((addr.s_addr & 0xFF) == 67 && (addr.s_addr & 0xFF00) >> 8 == 194) ||
        		((addr.s_addr & 0xFF) == 35 && (addr.s_addr & 0xFF00) >> 8 == 0) ||
                (addr.s_addr & 0xFF) == 10) ? true : false;

    //    return ((addr.s_addr & 0xFF) == 10) ? true : false;
}

void FlowAbstract::runMeasureTask(Context& traceCtx, const struct pcap_pkthdr *header, const u_char *pkt_data) {
	if (is_first) {
		this->ETHER_HDR_LEN = traceCtx.getEtherLen();
		is_first = false;
		start_time_sec = header->ts.tv_sec;
		last_time_sec = start_time_sec;
		end_time_sec = start_time_sec;

		//if (RUNNING_LOCATION == RLOC_CONTROL_SERVER || RUNNING_LOCATION == RLOC_CONTROL_CLIENT) {
			TIME_BASE = (double)(header->ts.tv_sec) + (double)header->ts.tv_usec / (double)USEC_PER_SEC;
		//}
		//cout << "TIME_BASE " << fixed << TIME_BASE << endl;
	} else {
		end_time_sec = header->ts.tv_sec;
	}

	ts = ((double)(header->ts.tv_sec) + (double)header->ts.tv_usec / (double)USEC_PER_SEC);// - TIME_BASE;

	traceCtx.updateContext(ts);

	if (*((u_short *)(pkt_data + ETHER_HDR_LEN - 2)) == ETHERTYPE_IP) {
		//all IP
		pip = (ip *)(pkt_data + ETHER_HDR_LEN);
		b1 = isClient(pip->ip_src);
		b2 = isClient(pip->ip_dst);
		int appIndex = -1;
		appIndex = *((u_short *)(pkt_data + 6)) & 0xFF;

		string appName("none");
		if (appIndex < traceCtx.getAppNameMap().size()) {
			appName.assign(traceCtx.getAppNameByIndex(appIndex));
		}
		// cout << appIndex << endl;
		if ((b1 && !b2) || (!b1 && b2)) { //uplink or downlink
			if (b1 && !b2) { // uplink
				ip_clt = pip->ip_src.s_addr;
				ip_svr = pip->ip_dst.s_addr;
			} else { //downlink
				ip_clt = pip->ip_dst.s_addr;
				ip_svr = pip->ip_src.s_addr;
			}
		} else if (b1 && b2) { //ignore 1, both are client IP
			ignore_count1++;
		} else { //ignore 2, none are client IP
			ignore_count2++;
		}

		//init userp

		userp = &(users[traceCtx.getUserID()]);

		userp->userID.assign(traceCtx.getUserID());
		if (userp->start_time == 0) {
			//init
			userp->start_time = ts;
		}

		switch (pip->ip_p) {
			case IPPROTO_TCP:
				tcp_count++;
				ptcp = (tcphdr *)((u_char *)pip + BYTES_PER_32BIT_WORD * pip->ip_hl); //cast of u_char* is necessary
				payload_len = bswap16(pip->ip_len) - BYTES_PER_32BIT_WORD * (pip->ip_hl + ptcp->doff);

				opt_len = BYTES_PER_32BIT_WORD * ptcp->doff - 20;
				opt_ts = (u_int *)((u_char *)ptcp + 20);
				window_scale = 0;

				// TCP options
				while (opt_len >= 10) { //Timestamps option at least 10 bytes
					if ((*((u_char *)opt_ts)) == 0x08 && (*(((u_char *)opt_ts) + 1)) == 0x0a) {
						opt_ts = (u_int *)((u_char *)opt_ts + 2);
						opt_len = 100;
						break;
					} else if ((*((u_char *)opt_ts)) == 0x00 || (*((u_char *)opt_ts)) == 0x01) {
						//NOP
						opt_ts = (u_int *)((u_char *)opt_ts + 1); //opt_ts + 1 is length field
						opt_len--;
					} else {
						if ((*((u_char *)opt_ts)) == 0x03) {
							//window scale option in the SYN packet
							window_scale = (1 << (*((u_int *)((u_char *)opt_ts + 2))));
						}
						jump = (u_int)(*((u_char *)opt_ts + 1));
						if (jump > opt_len || jump <= 0) {
							//something weird happens
							opt_len = 0;
							break;
						}
						opt_len -= jump;
						opt_ts = (u_int *)((u_char *)opt_ts + jump); //opt_ts + 1 is length field
					}
				} // tcp options

				if (traceType.compare("-1")==0) {
				/* end traceType == -1 */
				} else if (traceType.compare(CONFIG_PARAM_TRACE_DEV)==0) {
					// Port number
					if (b1 && !b2) { // uplink
						port_clt = bswap16(ptcp->source);
						port_svr = bswap16(ptcp->dest);

						tcp_up_bytes += payload_len;

					} else if (!b1 && b2) { //downlink
						port_clt = bswap16(ptcp->dest);
						port_svr = bswap16(ptcp->source);

						tcp_down_bytes += payload_len;

					} else {
						break;
					}

					//flow statistics analysis

					flow_index = port_clt * (((uint64)1) << 32) + ip_clt;
					flow_it_tmp = client_flows.find(flow_index);

					char buf[50];
					//sprintf(buf, "%.6f %" PRIu64 "", ts, flow_index);
					sprintf(buf, "%.6f", ts);

					if (flow_it_tmp != client_flows.end()) {
						flow = &(client_flows[flow_index]);
						//found flow
					//} else {
					} else if (flow_it_tmp == client_flows.end() && (ptcp->syn) != 0 && (b1 && !b2)) {
						//no flow found, now uplink SYN packet
						//cout << "new flow: " << appName << " " << flow_index <<  endl;
						client_flows[flow_index].clt_ip = ip_clt; //init a flow
						flow_count++;

						flow = &client_flows[flow_index];
						userp->tcp_flows[flow_index] = flow;
						flow->flowIndex = flow_index;
						flow->idle_time_before_syn = ts - userp->last_packet_time;
						flow->svr_ip = ip_svr;
						flow->clt_port = port_clt;
						flow->svr_port = port_svr;
						flow->start_time = ts;
						flow->end_time = ts;
						flow->last_data_ts = ts;


						// new burst/background notification

						if (userp->appTimeLog.find(appName) == userp->appTimeLog.end()) {
							if (!traceCtx.isScreenOn() ||
									(traceCtx.isScreenOn() && !traceCtx.isForeground(appName))) {
								userp->appTimeLog[appName] = "";
								userp->appTimeLog[appName] += buf;
								userp->appTimeLog[appName] += "\n";
							}
							userp->appTime[appName] = 0;
						} else if (ts - userp->appTime[appName] > this->BURST_THRESHOLD) {
							if (!traceCtx.isScreenOn() ||
								(traceCtx.isScreenOn() && !traceCtx.isForeground(appName))) {
								userp->appTimeLog[appName] += buf;
								userp->appTimeLog[appName] += "\n";
							}
						}

						if (client_flows.size() >= 100000 && ts - last_prune_time >= FLOW_MAX_IDLE_TIME / 2) {
						//if (ts - last_prune_time >= FLOW_MAX_IDLE_TIME) {
							cout << "Flowsize " << ts << " " << client_flows.size() << endl;
							last_prune_time = ts; //only prune once for every 100 seconds
							for (flow_it = client_flows.begin() ; flow_it != client_flows.end() ; ) {
								flow_it_tmp = flow_it;
								flow_it++;
								if (flow_it_tmp->second.end_time < ts - FLOW_MAX_IDLE_TIME) {
									//delete a flow
									//flow_it_tmp->second.print(-1 * ptcp->th_flags);
									users[flow_it_tmp->second.userID].tcp_flows.erase(flow_it_tmp->second.flowIndex);
									client_flows.erase(flow_it_tmp);
								}
							}//*/
							map<string, user>::iterator user_it;
							for (user_it = users.begin(); user_it != users.end(); user_it++) {
								user *tmp_user = &(user_it->second);
								map<string, string>::iterator log_it;
								for (log_it = tmp_user->appTimeLog.begin();
										log_it != tmp_user->appTimeLog.end(); log_it++) {
									string f_name("tslog__");
									f_name += user_it->first;
									f_name += "__";
									f_name += log_it->first;
									ofstream f_output(f_name.c_str(), ios::app);
									f_output << log_it->second;
									f_output.close();
								}
								tmp_user->appTimeLog.clear();
							}
						}
					} else {
						//no flow found and not link SYN packet
						//could be ACKs after RST/FIN packets
						//could be packets for long lived TCP flow
						//just ignore
						break;
					}

					flow = &client_flows[flow_index];
					flow->end_time = ts;
					flow->packet_count++; //should be before the SYN-RTT analysis

					//if a terminate flow packet is here, terminate flow and output flow statistics
					if ((ptcp->fin) != 0 || (ptcp->rst) != 0) {
						//flow->print((ptcp->fin) | (ptcp->rst));
						flow->last_data_ts = ts;
						//delete this flow
						userp->tcp_flows.erase(flow_index);
						client_flows.erase(flow_index);
						break;
					} else { // all packets of this flow goes to here except for the FIN and RST packets
						if (b1 && !b2) { // uplink
							if (payload_len > 0) {
								// data
								if (ts - flow->last_data_ts > this->BURST_THRESHOLD) {
									//cout << "uplink " << appName << " " << flow_index << " " << ts << " " << flow->last_data_ts <<  endl;
									if (userp->appTimeLog.find(appName) == userp->appTimeLog.end()) {
										if (!traceCtx.isScreenOn() || (traceCtx.isScreenOn() && !traceCtx.isForeground(appName))) {
											userp->appTimeLog[appName] = "";
											userp->appTimeLog[appName] += buf;
											userp->appTimeLog[appName] += "\n";
										}
									} else if (ts - userp->appTime[appName] > this->BURST_THRESHOLD) {
										if (!traceCtx.isScreenOn() || (traceCtx.isScreenOn() && !traceCtx.isForeground(appName))) {
											userp->appTimeLog[appName] += buf;
											userp->appTimeLog[appName] += "\n";
										}
									}
								}
							}

						} else if (!b1 && b2) { //downlink
							if (payload_len > 0) {
								// data
								if (ts - flow->last_data_ts > this->BURST_THRESHOLD) {
									//cout << "downlink " << appName << " " << flow_index << " " << ts << " " << flow->last_data_ts <<  endl;
									if (userp->appTimeLog.find(appName) == userp->appTimeLog.end()) {
										if (!traceCtx.isScreenOn() || (traceCtx.isScreenOn() && !traceCtx.isForeground(appName))) {
											userp->appTimeLog[appName] = "";
											userp->appTimeLog[appName] += buf;
											userp->appTimeLog[appName] += "\n";
										}
									} else if (ts - userp->appTime[appName] > this->BURST_THRESHOLD) {
										if (!traceCtx.isScreenOn() || (traceCtx.isScreenOn() && !traceCtx.isForeground(appName))) {
											userp->appTimeLog[appName] += buf;
											userp->appTimeLog[appName] += "\n";
										}
									}
								}
							}
						}
					}
					flow->last_data_ts = ts;
					userp->appTime[appName] = ts;
					/* end traceType == CONFIG_PARAM_TRACE_DEV */
				}

				break;
			case IPPROTO_UDP:
				break;
			case IPPROTO_ICMP:
				break;
			default:
				break;
		}

		//everything is in IP

		userp->last_packet_time = ts;

	} else {
		no_ip_count++;
		//cout << "Packet " << packet_count << " not IP " << peth->ether_type << endl;
	}

	//if (packet_count > 1000)
	//    exit(0);

/*	vector<MeasureTask>::iterator it;
	for (it = mMeasureTask.begin(); it != mMeasureTask.end(); it++) {
		it->procPacket(this, header, pkt_data);
	}*/
}

void FlowAbstract::runCleanUp() {
	map<string, user>::iterator user_it;
	for (user_it = users.begin(); user_it != users.end(); user_it++) {
		user *tmp_user = &(user_it->second);
		map<string, string>::iterator log_it;
		for (log_it = tmp_user->appTimeLog.begin();
				log_it != tmp_user->appTimeLog.end(); log_it++) {
			string f_name("tslog__");
			f_name += user_it->first;
			f_name += "__";
			f_name += log_it->first;
			ofstream f_output(f_name.c_str(), ios::app);
			f_output << log_it->second;
			f_output.close();
		}
		tmp_user->appTimeLog.clear();
	}
}
