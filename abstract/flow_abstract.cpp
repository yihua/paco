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
	packet_count = 0;
}

void FlowAbstract::configTraceType(string type) {
	traceType = type;
}

string FlowAbstract::getTraceType() {
	return traceType;
}

string FlowAbstract::intToString(int x) {
	char s[24];
	sprintf(s, "%d", x);
	string ss(s);
	return ss;
}

bool FlowAbstract::isClient(in_addr addr) {
		if (ConfigParam::isSameTraceType(traceType, CONFIG_PARAM_TRACE_DEV))
    	//for Yihua's trace, server trace: client is 198.*; client trace: client is 10.*; and 32.* for 3G trace
        	return (((addr.s_addr & 0xFF000000) >> 24 == 192 && (addr.s_addr & 0xFF0000) >> 16 == 168) ||
        			((addr.s_addr & 0xFF000000) >> 24 == 67 && (addr.s_addr & 0xFF0000) >> 16 == 194) ||
        			((addr.s_addr & 0xFF000000) >> 24 == 35 && (addr.s_addr & 0xFF0000) >> 16 == 0) ||
                	(addr.s_addr & 0xFF000000) >> 24 == 10) ? true : false;
        else if (ConfigParam::isSameTraceType(traceType, CONFIG_PARAM_TRACE_ATT_SPGW) ||
        	ConfigParam::isSameTraceType(traceType, CONFIG_PARAM_TRACE_ATT_ENB))
    	    return ((addr.s_addr & 0xFF000000) >> 24 == 10) ? true : false;
    	else
    		return (((addr.s_addr & 0xFF000000) >> 24 == 192 && (addr.s_addr & 0xFF0000) >> 16 == 168) ||
        			((addr.s_addr & 0xFF000000) >> 24 == 67 && (addr.s_addr & 0xFF0000) >> 16 == 194) ||
        			((addr.s_addr & 0xFF000000) >> 24 == 35 && (addr.s_addr & 0xFF0000) >> 16 == 0) ||
                	(addr.s_addr & 0xFF000000) >> 24 == 10) ? true : false;
}

bool FlowAbstract::isControlledServer(in_addr addr) {
	if (ConfigParam::isSameTraceType(traceType, CONFIG_PARAM_TRACE_DEV)) {
		if ((addr.s_addr & 0xFF000000) >> 24 == 141 && (addr.s_addr & 0xFF0000) >> 16 == 212) {
			//cout << "141.212." << ((addr.s_addr & 0xFF00) >> 8)
			//  << "."<< (addr.s_addr & 0xFF) << endl;
			return true;
		}
	}
	return false;
}

void FlowAbstract::printAddr(in_addr addr1, in_addr addr2) {
	cout << ((addr1.s_addr & 0xFF000000) >> 24) << "." << ((addr1.s_addr & 0xFF0000) >> 16)
		<< "." << ((addr1.s_addr & 0xFF00) >> 8) << "." << (addr1.s_addr & 0xFF)
		<< " | " << ((addr2.s_addr & 0xFF000000) >> 24) << "." << ((addr2.s_addr & 0xFF0000) >> 16)
                << "." << ((addr2.s_addr & 0xFF00) >> 8) << "." << (addr2.s_addr & 0xFF) << endl;
}

void FlowAbstract::bswapIP(struct ip* ip) {
	ip->ip_len=bswap16(ip->ip_len);
	ip->ip_id=bswap16(ip->ip_id);
	ip->ip_off=bswap16(ip->ip_off);
	ip->ip_sum=bswap16(ip->ip_sum);
	ip->ip_src.s_addr=bswap32(ip->ip_src.s_addr);
	ip->ip_dst.s_addr=bswap32(ip->ip_dst.s_addr);
}
void FlowAbstract::bswapTCP(struct tcphdr* tcphdr) {
	tcphdr->source=bswap16(tcphdr->source);
	tcphdr->dest=bswap16(tcphdr->dest);
	tcphdr->window=bswap16(tcphdr->window);
	tcphdr->check=bswap16(tcphdr->check);
	tcphdr->urg_ptr=bswap16(tcphdr->urg_ptr);
	tcphdr->seq=bswap32(tcphdr->seq);
	tcphdr->ack_seq=bswap32(tcphdr->ack_seq);
}
void FlowAbstract::bswapUDP(struct udphdr* udphdr) {
	udphdr->source=bswap16(udphdr->source);
	udphdr->dest=bswap16(udphdr->dest);
	udphdr->len=bswap16(udphdr->len);
	udphdr->check=bswap16(udphdr->check);
}

void FlowAbstract::bswapGTP(gtphdr* gtphdr){
	gtphdr->len = bswap16(gtphdr->len);
	gtphdr->teid = bswap32(gtphdr->teid);
}

void FlowAbstract::writeTCPFlowStat(Result* result, const TCPFlow* tcpflow) {
	int size = tcpflow->content_type.size() + tcpflow->user_agent.size() +
				tcpflow->host.size() + tcpflow->content_length.size() + 1000;
	char buf[size];
	sprintf(buf, "%s %ld %s %d.%d.%d.%d:%d %d.%d.%d.%d:%d \
%.6lf %.6lf %.6lf %.6lf %.6lf %.6lf \
%lld %lld %lld %lld %.6lf %.6lf %.6lf %lld %lld \
%lld %lld %lld %lld \
%d %s %s %s %s %d\n",
		userp->userID.c_str(), userp->tcp_flows.size(),
		tcpflow->flowIndex.c_str(), 
		(tcpflow->clt_ip)>>24, (tcpflow->clt_ip)>>16 & 0xFF, (tcpflow->clt_ip)>>8 & 0xFF, (tcpflow->clt_ip) & 0xFF,
		tcpflow->clt_port,
		(tcpflow->svr_ip)>>24, (tcpflow->svr_ip)>>16 & 0xFF, (tcpflow->svr_ip)>>8 & 0xFF, (tcpflow->svr_ip) & 0xFF,
		tcpflow->svr_port,
		tcpflow->start_time, tcpflow->tmp_start_time,
		tcpflow->first_ul_pl_time, tcpflow->first_dl_pl_time,
		tcpflow->last_ul_pl_time, tcpflow->last_dl_pl_time,
		tcpflow->total_ul_payload, tcpflow->total_dl_payload,
    	tcpflow->total_ul_whole, tcpflow->total_dl_whole,
    	tcpflow->ul_time, tcpflow->dl_time, tcpflow->last_tcp_ts,
    	tcpflow->total_ul_payload_h, tcpflow->total_dl_payload_h,
    	tcpflow->ul_rate_payload, tcpflow->dl_rate_payload,
    	tcpflow->ul_rate_payload_h, tcpflow->dl_rate_payload_h,
    	tcpflow->http_request_count,
    	tcpflow->content_type.c_str(), tcpflow->user_agent.c_str(),
    	tcpflow->host.c_str(), tcpflow->content_length.c_str(), 
		tcpflow->total_content_length);
	//cout << "write to string buf: " << string(buf).size() << endl;
	/*
	int tmp = string(buf).size();
	if (tmp > 999999) {
		cout << "write to string buf: " << tmp << endl;
		char* buf2 = new char[tmp+2];
		sprintf(buf2, "%s %ld %s %d.%d.%d.%d:%d %d.%d.%d.%d:%d \
		%.6lf %.6lf %.6lf %.6lf %.6lf %.6lf \
		%lld %lld %lld %lld %.6lf %.6lf %.6lf %lld %lld \
		%d %s %s %s %s %d\n",
		userp->userID.c_str(), userp->tcp_flows.size(),
		tcpflow->flowIndex.c_str(), 
		(tcpflow->clt_ip)>>24, (tcpflow->clt_ip)>>16 & 0xFF, (tcpflow->clt_ip)>>8 & 0xFF, (tcpflow->clt_ip) & 0xFF,
		tcpflow->clt_port,
		(tcpflow->svr_ip)>>24, (tcpflow->svr_ip)>>16 & 0xFF, (tcpflow->svr_ip)>>8 & 0xFF, (tcpflow->svr_ip) & 0xFF,
		tcpflow->svr_port,
		tcpflow->start_time, tcpflow->tmp_start_time,
		tcpflow->first_ul_pl_time, tcpflow->first_dl_pl_time,
		tcpflow->last_ul_pl_time, tcpflow->last_dl_pl_time,
		tcpflow->total_ul_payload, tcpflow->total_dl_payload,
    	tcpflow->total_ul_whole, tcpflow->total_dl_whole,
    	tcpflow->ul_time, tcpflow->dl_time, tcpflow->last_tcp_ts,
    	tcpflow->total_ul_payload_h, tcpflow->total_dl_payload_h,
    	tcpflow->http_request_count,
    	tcpflow->content_type.c_str(), tcpflow->user_agent.c_str(),
    	tcpflow->host.c_str(), tcpflow->content_length.c_str(), 
		tcpflow->total_content_length);
		result->addResultToFile(2, buf2);
	}*/
	
	result->addResultToFile(2, buf);
	//cout << "write to string buf end" << endl;
}

void FlowAbstract::writeSessionStat(Result* result, const User* user) {
	char buf[200];
	sprintf(buf, "%s %.6lf %.6lf %lld %lld %lld %lld %lld %lld\n",
		user->userID.c_str(),
		user->session_start_time, user->session_end_time,
		user->session_ip_all, user->session_ip_payload,
		user->session_tcp_all, user->session_tcp_payload,
		user->session_udp_all, user->session_udp_payload);
	result->addResultToFile(4, buf);
}

void FlowAbstract::writeRateStat(Result* result, const User* user) {
	char buf[200];
	sprintf(buf, "%s %.6lf %.6lf %lld %lld %lld %lld %lld %lld\n",
		user->userID.c_str(),
		user->bw_bin_start_time, user->bw_bin_start_time + USER_RATE_BIN,
		user->bw_bin_ip_all, user->bw_bin_ip_payload,
		user->bw_bin_tcp_all, user->bw_bin_tcp_payload,
		user->bw_bin_udp_all, user->bw_bin_udp_payload);
	result->addResultToFile(3, buf);
}

void FlowAbstract::runMeasureTask(Result* result, Context& traceCtx, const struct pcap_pkthdr *header, const u_char *pkt_data) {
	packet_count++;
	/*
	 * first packet ever. set the base time. maintain the time of the last packet.
	 */
	if (is_first) {
		this->ETHER_HDR_LEN = traceCtx.getEtherLen();
		is_first = false;
		start_time_sec = header->ts.tv_sec;
		last_time_sec = start_time_sec;
		end_time_sec = start_time_sec;

		TIME_BASE = (double)(header->ts.tv_sec) + (double)header->ts.tv_usec / (double)USEC_PER_SEC;
	} else {
		end_time_sec = header->ts.tv_sec;
	}

	/* timestamp of the packet (unit: second, accuracy: microsecond)
	*/
	ts = ((double)(header->ts.tv_sec) + (double)header->ts.tv_usec / (double)USEC_PER_SEC);// - TIME_BASE;

	/*
	 * update device context information
	 */
	traceCtx.updateContext(ts);
	bool doIPProcess = false;
	
	/* For user study and SPGW traces, there is no GTP headers.
	*/

	if ((ConfigParam::isSameTraceType(traceType, CONFIG_PARAM_TRACE_DEV) || 
		ConfigParam::isSameTraceType(traceType, CONFIG_PARAM_TRACE_ATT_SPGW)) && 
		*((u_short *)(pkt_data + ETHER_HDR_LEN - 2)) == ETHERTYPE_IP) {
		/*
		 * IP packet processing. Extract IP addresses and determine which one is the client IP
		 */
		ip_hdr = (ip *)(pkt_data + ETHER_HDR_LEN);
		doIPProcess = true;
	}

	/* For ENB traces, be aware of 802.1Q and GTP headers.
	* Use the IP headers in the GTP payload.
	*/
	if (ConfigParam::isSameTraceType(traceType, CONFIG_PARAM_TRACE_ATT_ENB)) {
		if (*((u_short *)(pkt_data + ETHER_HDR_LEN - 2)) == ETHERTYPE_8021Q) {
			ip_hdr = (ip *)(pkt_data + ETHER_HDR_LEN + VLAN_HDR_8021Q_LEN);
			if (*((u_short *)((u_char *)ip_hdr - 2)) == ETHERTYPE_IP) {
				udp_hdr = (udphdr *)(((u_char *)ip_hdr + BYTES_PER_32BIT_WORD * ip_hdr->ip_hl));
#if BYTE_ORDER == LITTLE_ENDIAN
				bswapUDP(udp_hdr);
#endif
				//cout << udp_hdr->source << "\t" << udp_hdr->dest << endl;
				if (udp_hdr->source == 2152 || udp_hdr->dest == 2152) {
					gtp_hdr = (gtphdr *)((u_char *)udp_hdr + UDP_HDR_LEN);
					bswapGTP(gtp_hdr);
					if (gtp_hdr->ext > 0 || gtp_hdr->seq > 0 || gtp_hdr->pnb > 0)
						ip_hdr = (ip *)((u_char *)gtp_hdr + 12);
					else
						ip_hdr = (ip *)((u_char *)gtp_hdr + 8);
					/*
					if (packet_count < 100) {
						cout << packet_count << ":\t";
						cout << gtp_hdr->ver << "\t" << gtp_hdr->proto << "\t" 
							<< gtp_hdr->res1 << "\t" << gtp_hdr->ext << "\t"
							<< gtp_hdr->seq << "\t" << gtp_hdr->pnb << "\t"
							<< gtp_hdr->msg << "\t" << gtp_hdr->len << "\t" 
							<< gtp_hdr->teid << endl;
					}*/
					doIPProcess = true;
				} else {
					//cout << packet_count << "No GTP header!\t" 
					//	<< udp_hdr->source << "\t" << udp_hdr->dest << endl;
				}
			} else {
				cout << packet_count << "No IP header!\t" << *((u_short *)((u_char *)ip_hdr - 2)) << endl;
			}
		} else {
			cout << packet_count << "No 802.1Q header!" << endl;
		}
	}

	/*
	 * Layer 3 (Network Layer) process
	 */
	if (doIPProcess) {
		// do swap to correct byte order
#if BYTE_ORDER == LITTLE_ENDIAN
		bswapIP(ip_hdr);
#endif

		b1 = isClient(ip_hdr->ip_src);
		b2 = isClient(ip_hdr->ip_dst);
		//if (packet_count < 100) {
		//	printAddr(ip_hdr->ip_src, ip_hdr->ip_dst); 
		//}
		if (ConfigParam::isSameTraceType(traceType, CONFIG_PARAM_TRACE_DEV) && 
			(isControlledServer(ip_hdr->ip_src) || isControlledServer(ip_hdr->ip_dst)))
			return;
		
		int appIndex = -1;
		appIndex = *((u_short *)(pkt_data + 6)) & 0xFF;

		/* For user study trace, map the traffic to application name
		*/
		string appName("none");

		if (ConfigParam::isSameTraceType(traceType, CONFIG_PARAM_TRACE_DEV)) {
			//cout << "flow abtract dev" << endl;
			if (appIndex < traceCtx.getAppNameMap().size()) {
				appName.assign(traceCtx.getAppNameByIndex(appIndex));
			}
		}

		// cout << appIndex << endl;
		if ((b1 && !b2) || (!b1 && b2)) { //uplink or downlink
			if (b1 && !b2) { // uplink
				ip_clt = ip_hdr->ip_src.s_addr;
				ip_svr = ip_hdr->ip_dst.s_addr;
			} else { //downlink
				ip_clt = ip_hdr->ip_dst.s_addr;
				ip_svr = ip_hdr->ip_src.s_addr;
			}
		} else if (b1 && b2) { //ignore 1, both are client IP
			//cout << "ignore 1" << endl;
			ignore_count1++;
		} else { //ignore 2, none are client IP
			//cout << "ignore 2" << endl;
			ignore_count2++;
		}

		ip_whole_len = ip_hdr->ip_len;
		ip_payload_len = ip_hdr->ip_len - BYTES_PER_32BIT_WORD * (ip_hdr->ip_hl);

		//if (users.size() % 10000 == 0)
		//	cout << "users: " << users.size() << endl;

		/*
		 * differentiate different users
		 */
		if (ConfigParam::isSameTraceType(traceType, CONFIG_PARAM_TRACE_DEV)) {
			userp = &(users[traceCtx.getUserID()]);
			userp->userID.assign(traceCtx.getUserID());
		} else {
			userp = &(users[intToString((unsigned int)ip_clt)]);
			userp->userID.assign(intToString((unsigned int)ip_clt));
		}

		if (userp->start_time < 0) {
			//init
			userp->start_time = ts;
			
			// for concurrency statistics
			userp->cc_start = ts;
			userp->last_cc_sample_time = ts;
			userp->bw_bin_start_time = ts;
			userp->session_start_time = ts;
			userp->session_end_time = ts;

			if (ConfigParam::isSameTraceType(traceType, CONFIG_PARAM_TRACE_DEV) ||
				ConfigParam::isSameTraceType(traceType, CONFIG_PARAM_TRACE_ATT_ENB))
				userp->is_sample = true;
			else
				userp->is_sample = false;
		} else {
			// User throughput calculation (1s bin)
			if (ts > userp->bw_bin_start_time + USER_RATE_BIN) {
				writeRateStat(result, userp);
				userp->bw_bin_start_time = ts;
				userp->resetRateStat();
			}

			userp->bw_bin_ip_all += ip_whole_len;
    		userp->bw_bin_ip_payload += ip_payload_len;

			// User session process
    		if (ts - userp->session_end_time > USER_SESSION_IDLE) {
    			writeSessionStat(result, userp);
    			userp->session_start_time = ts;
    			userp->session_end_time = ts;
    			userp->resetSessionStat();
    		}
    		userp->session_ip_all += ip_whole_len;
    		userp->session_ip_payload += ip_payload_len;
    	}

		/* TCP Concurrency statistics*/
		if (ConfigParam::isSameTraceType(traceType, CONFIG_PARAM_TRACE_ATT_SPGW) &&
			ts - userp->last_cc_sample_time > CC_SAMPLE_PERIOD &&
			!userp->is_sample) {
			userp->is_sample = true;
			userp->cc_start = ts;
			userp->last_cc_sample_time = ts + CC_SAMPLE_PERIOD;
		}
		
		if (userp->is_sample && ts - userp->cc_start > 1.0) {
			int conn_d_data = 0, conn_d_ack = 0, conn_u_data = 0, conn_u_ack = 0, overlap = 0;
			bool flag = false;
			//cout << "flows: " << userp->tcp_flows.size() << endl;
			for (flow_it = userp->tcp_flows.begin(); flow_it != userp->tcp_flows.end();) {
				flag = false;
				if (flow_it->second->last_ul_pl_time >= userp->cc_start &&
					flow_it->second->last_ul_pl_time < userp->cc_start + 1.0) {
					conn_u_data++;
					flag = true;
				} else if (flow_it->second->last_dl_ack_time >= userp->cc_start &&
					flow_it->second->last_dl_ack_time < userp->cc_start + 1.0) {
					conn_d_ack++;
					flag = true;
				}

				if (flow_it->second->last_dl_pl_time >= userp->cc_start &&
					flow_it->second->last_dl_pl_time < userp->cc_start + 1.0) {
					conn_d_data++;
					if (flag)
						overlap++;
				} else if (flow_it->second->last_ul_ack_time >= userp->cc_start &&
					flow_it->second->last_ul_ack_time < userp->cc_start + 1.0) {
					conn_u_ack++;
					if (flag)
						overlap++;
				}

				if (userp->cc_start - flow_it->second->last_tcp_ts > FLOW_MAX_IDLE_TIME) {
					//cout << packet_count << " write" << endl;
					writeTCPFlowStat(result, flow_it->second);
					//cout << packet_count << " erase" << endl;
					userp->tcp_flows.erase(flow_it++);
					//cout << "write finish" << endl;
					//flow_it++;
				} else if (userp->cc_start > flow_it->second->last_tcp_ts && 
					flow_it->second->flow_finish) {
					writeTCPFlowStat(result, flow_it->second);
					userp->tcp_flows.erase(flow_it++);
				} else {
					flow_it++;
				}
			}
			if (conn_d_data + conn_d_ack + conn_u_data + conn_u_ack > 0) {
				char buf[100];
				sprintf(buf, "%s %.6lf %d %d %d %d %d\n", userp->userID.c_str(), userp->cc_start,
						conn_d_data, conn_d_ack, conn_u_data, conn_u_ack, overlap);
				result->addResultToFile(1, buf);
			}
			while (ts - userp->cc_start > 1.0)
				userp->cc_start += 1.0;
			if (ConfigParam::isSameTraceType(traceType, CONFIG_PARAM_TRACE_ATT_SPGW))
				userp->is_sample = false;
		}
		/*
		 * Layer 4 (Transport Layer) processing
		 */
		switch (ip_hdr->ip_p) {
			/*
			 * TCP traffic
			 */
			case IPPROTO_TCP:
				tcp_count++;
				tcp_hdr = (tcphdr *)((u_char *)ip_hdr + BYTES_PER_32BIT_WORD * ip_hdr->ip_hl); //cast of u_char* is necessary
				// do swap for TCP header
				bswapTCP(tcp_hdr);

				payload_len = ip_hdr->ip_len - BYTES_PER_32BIT_WORD * (ip_hdr->ip_hl + tcp_hdr->doff);
				tcp_whole_len = ip_hdr->ip_len - BYTES_PER_32BIT_WORD * (ip_hdr->ip_hl);

				userp->bw_bin_tcp_all += tcp_whole_len;
				userp->bw_bin_tcp_payload += payload_len;
				userp->session_tcp_all += tcp_whole_len;
				userp->session_tcp_payload += payload_len;

				opt_len = BYTES_PER_32BIT_WORD * tcp_hdr->doff - 20;
				opt_ts = (u_int *)((u_char *)tcp_hdr + 20);
				window_scale = 0;

				/*
				 * TCP options. Timestamps option at least 10 bytes
				 */
				while (opt_len >= 10) {
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
				} else {//if (traceType.compare(CONFIG_PARAM_TRACE_DEV)==0) {
					// Port number
					if (b1 && !b2) { // uplink
						port_clt = tcp_hdr->source;
						port_svr = tcp_hdr->dest;

						tcp_up_bytes += payload_len;

					} else if (!b1 && b2) { //downlink
						port_clt = tcp_hdr->dest;
						port_svr = tcp_hdr->source;

						tcp_down_bytes += payload_len;

					} else {
						break;
					}

					/*
					 * flow statistics analysis
					 */

					//flow_index = port_clt * (((uint64)1) << 32) + ip_clt;
					if (ip_clt < ip_svr)
						flow_index = intToString(ip_clt) + ":" + intToString(port_clt) + "|" +
										intToString(ip_svr) + ":" + intToString(port_svr);
					else
						flow_index = intToString(ip_svr) + ":" + intToString(port_svr) + "|" +
										intToString(ip_clt) + ":" + intToString(port_clt);

					flow_it_tmp = userp->tcp_flows.find(flow_index);

					//char buf[50];
					//sprintf(buf, "%.6f %" PRIu64 "", ts, flow_index);
					//sprintf(buf, "%.6f", ts);

					if (flow_it_tmp != userp->tcp_flows.end()) {
						flow = userp->tcp_flows[flow_index];
						//found flow
					//} else {
					} else if (flow_it_tmp == userp->tcp_flows.end() && (tcp_hdr->syn) != 0 && (b1 && !b2)) {
						//no flow found, now uplink SYN packet
						//cout << "new flow: " << appName << " " << flow_index <<  endl;
						userp->tcp_flows[flow_index] = new TCPFlow();
						flow = userp->tcp_flows[flow_index];

						flow->clt_ip = ip_clt; //init a flow
						flow_count++;

						//userp->tcp_flows[flow_index] = flow;
						flow->flowIndex = flow_index;
						flow->idle_time_before_syn = ts - userp->last_packet_time;
						flow->svr_ip = ip_svr;
						flow->clt_port = port_clt;
						flow->svr_port = port_svr;
						flow->start_time = ts;
						flow->end_time = ts;
						flow->last_tcp_ts = ts;
						flow->tmp_start_time = -1;


						// new burst/background notification
						/*
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
						}*/
								/*
						if (client_flows.size() >= 100000 && ts - last_prune_time >= FLOW_MAX_IDLE_TIME / 2) {
						//if (ts - last_prune_time >= FLOW_MAX_IDLE_TIME) {
							cout << "Flowsize " << ts << " " << client_flows.size() << endl;
							last_prune_time = ts; //only prune once for every 100 seconds
							for (flow_it = client_flows.begin() ; flow_it != client_flows.end() ; ) {
								flow_it_tmp = flow_it;
								flow_it++;
								if (flow_it_tmp->second.end_time < ts - FLOW_MAX_IDLE_TIME) {
									//delete a flow
									//flow_it_tmp->second.print(-1 * tcp_hdr->th_flags);
									users[flow_it_tmp->second.userID].tcp_flows.erase(flow_it_tmp->second.flowIndex);
									client_flows.erase(flow_it_tmp);
								}
							}//*/
							/*
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
							}*/
						//}
					} else {
						//no flow found and not link SYN packet
						//could be ACKs after RST/FIN packets
						//could be packets for long lived TCP flow
						//just ignore
						if (payload_len > 0 && 
							(tcp_hdr->fin) == 0 && 
							(tcp_hdr->rst) == 0) {
							userp->tcp_flows[flow_index] = new TCPFlow();
							flow = userp->tcp_flows[flow_index];

							flow->clt_ip = ip_clt; //init a flow
							//flow_count++;

							//userp->tcp_flows[flow_index] = flow;
							flow->tmp_start_time = ts;
							flow->flowIndex = flow_index;
							flow->idle_time_before_syn = ts - userp->last_packet_time;
							flow->svr_ip = ip_svr;
							flow->clt_port = port_clt;
							flow->svr_port = port_svr;
							flow->start_time = -1.0;
							flow->end_time = ts;
							flow->last_tcp_ts = ts;
						} else {
							break;
						}
					}

					//flow = &client_flows[flow_index];
					flow->end_time = ts;
					flow->packet_count++; //should be before the SYN-RTT analysis

					flow->last_tcp_ts = ts;

					//if a terminate flow packet is here, terminate flow and output flow statistics
					if ((tcp_hdr->fin) != 0 || (tcp_hdr->rst) != 0) {
						//flow->print((tcp_hdr->fin) | (tcp_hdr->rst));
						flow->last_tcp_ts = ts;
						flow->flow_finish = true;
						//delete this flow
						//writeTCPFlowStat(result, flow);
						//userp->tcp_flows.erase(flow_index);
						//client_flows.erase(flow_index);
						break;
					} else if (!(flow->flow_finish)) { // all packets of this flow goes to here except for the FIN and RST packets
						if (b1 && !b2) { // uplink:0
							if (payload_len > 0) {
								if (flow->last_pl_dir == 0 &&
									ts - flow->last_payload_time < MAX_PKT_INTERARRIVAL) {
									flow->ul_time += (ts - flow->last_payload_time);
									flow->ul_rate_payload += flow->last_payload;
									flow->ul_rate_payload_h += flow->last_payload_h;
								}

								flow->last_payload = payload_len;
								flow->last_pl_dir = 0;
								flow->last_payload_time = ts;
								flow->total_ul_payload += payload_len;
								flow->total_ul_payload_h += tcp_whole_len;
 	 		  					flow->last_ul_pl_time = ts;
 	 		  					if (flow->first_ul_pl_time < 0) {
 	 		  						flow->first_ul_pl_time = ts;
 	 		  					}

								// data
								/*
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
								}*/
							} else { //ACK
								flow->last_ul_ack_time = ts;
							}
							if (tcp_whole_len > 0) {
								flow->total_ul_whole += tcp_whole_len;
							}
						} else if (!b1 && b2) { //downlink:1
							if (payload_len > 0) {
								if (flow->last_pl_dir == 1 &&
									ts - flow->last_payload_time < MAX_PKT_INTERARRIVAL) {
									flow->dl_time += (ts - flow->last_payload_time);
									flow->dl_rate_payload += flow->last_payload;
									flow->dl_rate_payload += flow->last_payload_h;
								}

								flow->last_payload = payload_len;
								flow->last_pl_dir = 1;
								flow->last_payload_time = ts;
								flow->total_dl_payload += payload_len;
								flow->total_dl_payload_h += tcp_whole_len;
 	 		  					flow->last_dl_pl_time = ts;
 	 		  					if (flow->first_dl_pl_time < 0) {
 	 		  						flow->first_dl_pl_time = ts;
 	 		  					}
								// data
								/*
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
								}*/
							} else { //ACK
								flow->last_dl_ack_time = ts;
							}
							if (tcp_whole_len > 0) {
								flow->total_dl_whole += tcp_whole_len;
							}
						}
					}

					/*
					 * RTT and TCP pattern analysis
					 */
					/*
					if (b1 && !b2) { // uplink
                        flow->update_seq_x(tcp_hdr->seq, payload_len, ts);
					} else if (!b1 && b2) {
                        flow->window_size = flow->window_scale * tcp_hdr->window;
                        //cout << setprecision(16) << ts;
                        //cout << " " << flow->ConvertIPToString(ip_hdr->ip_src.s_addr);
                        //cout << " " << flow->ConvertIPToString(ip_hdr->ip_dst.s_addr);
                        //cout << " " << tcp_hdr->seq << " " << tcp_hdr->ack_seq << endl;
						flow->update_ack_x(tcp_hdr->ack_seq, payload_len, ts);
					}*/

					if (ConfigParam::isSameTraceType(traceType, CONFIG_PARAM_TRACE_DEV)) {
						userp->appTime[appName] = ts;
					}

					/* end traceType == CONFIG_PARAM_TRACE_DEV */
			
					//HTTP analysis
                    if (ETHER_HDR_LEN + BYTES_PER_32BIT_WORD * (ip_hdr->ip_hl + tcp_hdr->doff) < header->caplen) {
                        //has TCP payload
                        payload = (char *)((char *)tcp_hdr + BYTES_PER_32BIT_WORD * tcp_hdr->doff);
                        payload_str = string(payload);
                        if (b1 && !b2) {
                            //UPLINK
                            if (payload_str.find("GET ") == 0 || payload_str.find("HEAD ") == 0 ||
                                payload_str.find("POST ") == 0 || payload_str.find("PUT ") == 0 ||
                                payload_str.find("DELETE ") == 0 || payload_str.find("TRACE ") == 0 ||
                                payload_str.find("OPTIONS ") == 0 || payload_str.find("CONNECT ") == 0 ||
                                payload_str.find("PATCH ") == 0) {
                                //uplink HTTP request
                                flow->http_request_count++;
                                string method, uri, host;
                                /*
                                if (appName.find("chrome", 0) >= 0 && appName.find("chrome", 0) < appName.length()) {
                                	int pos = 0, next_pos;
                                	bool uri_flag = false, host_flag = false;
                                	string s;
                                	while (pos >= 0) {
                                		next_pos = payload_str.find('\n', pos);
                                		if (next_pos < 0)
                                			break;
                                		s = payload_str.substr(pos, next_pos-pos);
                                		if ((!uri_flag) && (s.find("GET ") == 0 || s.find("HEAD ") == 0 ||
                                                s.find("POST ") == 0 || s.find("PUT ") == 0 ||
                                                s.find("DELETE ") == 0 || s.find("TRACE ") == 0 ||
                                                s.find("OPTIONS ") == 0 || s.find("CONNECT ") == 0 ||
                                                s.find("PATCH ") == 0)) {
                                			//cout << "Method:" << "\t" << s << endl;
                                			int pos1, pos2;
                                			pos1 = s.find(' ', 0);
                                			method = s.substr(0, pos1);
                                			pos2 = s.find(' ', pos1+1);
                                			uri = s.substr(pos1+1, pos2-pos1-1);
                                			uri_flag = true;
                                		}

                                		if ((!host_flag) && s.find("Host:") == 0) {
                                			//cout << "Hostline:" << "\t" << s << endl;
                                			int pos1 = s.find("\r", 0);
                                			if (pos1 < 0) {
                                				pos1 = s.length();
                                			}
                                			host = s.substr(6, pos1 - 6);
                                			host_flag = true;
                                		}

                                		if (uri_flag && host_flag) {
                                			break;
                                		}
                                		pos = next_pos+1;
                                	}
                                	string append_s("\n");
                                	//append_s += appName;
                                	//append_s += "\t";
                                	append_s += (host+uri);
                                	append_s += "\t";
                                	//append_s += method;
                                	//append_s += "\n";
                                	if (!userp->last_http_time > 0.1) {
                                		string append_ss("");
                                		append_ss += (host+uri);
                                		append_ss += "\t";
                                		OutputFile::append(userp->http_req_stat, userp->http_req_stat_size, 0, append_ss, "http_stat_output_", traceCtx.getUserID());
                                		//cout << ">>>>>>>>>>>>>>>>>>>>> " << traceCtx.getUserID() << "\t" << (host+uri) << endl;
                                	}
                                	else if (ts - userp->last_http_time > HTTP_THRESHOLD) {
                                		OutputFile::append(userp->http_req_stat, userperp->http_req_stat_size, ts - userp->last_http_time, append_s, "http_stat_output_", traceCtx.getUserID());
                                		//cout << ">>>>>>>>>>>>>>>>>>>>> " << traceCtx.getUserID() << "\t" << (host+uri) << "\t" << (ts - userp->last_http_time)*1000.0 << endl;
                                	}
                                	userp->last_http_time = ts;

                                	//cout << ts << "\t" << appName << "\t" << host+uri << "\t" << method << endl;
                            	} */

                                start_pos = payload_str.find("User-Agent: ");
                                end_pos = payload_str.find("\r\n", start_pos);
                                if (start_pos != string::npos && end_pos > start_pos + 12) {
                                	if (flow->first_user_agent.size() == 0) {
                                		flow->first_user_agent = compress_user_agent(payload_str.substr(start_pos + 12, end_pos - start_pos - 12));
                                    	flow->user_agent += flow->first_user_agent;
                                    	flow->user_agent += "|";
                                	} else {
                                		if (compress_user_agent(payload_str.substr(start_pos + 12, end_pos - start_pos - 12)).compare(flow->first_user_agent) == 0) {
                                			flow->user_agent += "*|";
                                		} else {
                                			flow->first_user_agent = compress_user_agent(payload_str.substr(start_pos + 12, end_pos - start_pos - 12));
                                    		flow->user_agent += flow->first_user_agent;
                                    		flow->user_agent += "|";
                                		}
                                	}
                                } else
                                	flow->user_agent += "|";

                                start_pos = payload_str.find("Host: ");
                                end_pos = payload_str.find("\r\n", start_pos);
                                if (start_pos != string::npos && end_pos > start_pos + 6) {
                                	if (flow->first_host.size() == 0) {
                                		flow->first_host = trim_string(payload_str.substr(start_pos + 6, end_pos - start_pos - 6));
                                    	flow->host += flow->first_host;
                                    	flow->host += "|";
                                    } else {
                                    	if (trim_string(payload_str.substr(start_pos + 6, end_pos - start_pos - 6)).compare(flow->first_host) == 0) {
                                    		flow->host += "*|";
                                    	} else {
                                    		flow->first_host = trim_string(payload_str.substr(start_pos + 6, end_pos - start_pos - 6));
                                    		flow->host += flow->first_host;
                                    		flow->host += "|";
                                    	}
                                    }
                                }
                                else
                                	flow->host += "|";

                            } //else if (appName.find("chrome", 0) >= 0 && appName.find("chrome", 0) < appName.length()) {
                            //	userp->last_http_time = ts;
                            //}
                        } else if (!b1 && b2) {
                            //DOWNLINK
                        	//if (appName.find("chrome", 0) >= 0 && appName.find("chrome", 0) < appName.length()) {
                        	//	userp->last_http_time = ts;
                        	//}
                            if (payload_str.find("HTTP/1.1 200 OK") == 0 || payload_str.find("HTTP/1.0 200 OK") == 0) {
                                //downlink HTTP 200 OK


                                start_pos = payload_str.find("Content-Type: ");
                                end_pos = payload_str.find("\r\n", start_pos);
                                if (start_pos != string::npos && end_pos > start_pos + 14) {
                                	if (flow->first_content_type.size() == 0) {
                                		flow->first_content_type = process_content_type(payload_str.substr(start_pos + 14, end_pos - start_pos - 14));
                                    	flow->content_type += flow->first_content_type;
                                    	flow->content_type += "|"; 
                                    } else {
                                    	if (process_content_type(payload_str.substr(start_pos + 14, end_pos - start_pos - 14)).compare(flow->first_content_type) == 0) {
                                    		flow->content_type += "*|"; 
                                    	} else {
                                    		flow->first_content_type = process_content_type(payload_str.substr(start_pos + 14, end_pos - start_pos - 14));
                                    		flow->content_type += flow->first_content_type;
                                    		flow->content_type += "|"; 
                                    	}
                                    }
                                } else {
                                	flow->content_type += "|";
                                }

                                start_pos = payload_str.find("Content-Length: ");
                                end_pos = payload_str.find("\r\n", start_pos);
                                if (start_pos != string::npos && end_pos > start_pos + 16) {
                                	flow->content_length += trim_string(payload_str.substr(start_pos + 16, end_pos - start_pos - 16));
                                	flow->content_length += "|";
                                    flow->total_content_length += StringToNumber<int>(trim_string(payload_str.substr(start_pos + 16, end_pos - start_pos - 16)));
                                } else {
                                	flow->content_length += "|";
                                }

                            //} else if (payload_str.find("HTTP/") == 0 && payload_str.find("200 OK") != -1) {
                             //   cout << "HTTP_RESPONSE_SPECIAL " << payload_str << endl;
                            }
                        }
                    }
				}

				break;
			case IPPROTO_UDP:
				udp_hdr = (udphdr *)((u_char *)ip_hdr + BYTES_PER_32BIT_WORD * ip_hdr->ip_hl);
				bswapUDP(udp_hdr);

				userp->bw_bin_udp_all += udp_hdr->len;
				userp->bw_bin_udp_payload += (udp_hdr->len-UDP_HDR_LEN);
				userp->session_udp_all += udp_hdr->len;
				userp->session_udp_payload += (udp_hdr->len-UDP_HDR_LEN);
				//if (udp_hdr->source == 53 || udp_hdr->dest == 53)
				//	cout << "dns" << endl;
				//break;
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

void FlowAbstract::runCleanUp(Result* result) {
	for (user_it = users.begin(); user_it != users.end(); user_it++) {
		User *tmp_user = &(user_it->second);
		//map<string, string>::iterator log_it;
		for (flow_it = tmp_user->tcp_flows.begin(); flow_it != tmp_user->tcp_flows.end();) {
			writeTCPFlowStat(result, flow_it->second);
			tmp_user->tcp_flows.erase(flow_it++);
		}

		writeSessionStat(result, tmp_user);
		/*for (log_it = tmp_user->appTimeLog.begin();
				log_it != tmp_user->appTimeLog.end(); log_it++) {
			string f_name("tslog__");
			f_name += user_it->first;
			f_name += "__";
			f_name += log_it->first;
			ofstream f_output(f_name.c_str(), ios::app);
			f_output << log_it->second;
			f_output.close();
		}*/
		tmp_user->appTimeLog.clear();
	}
}
