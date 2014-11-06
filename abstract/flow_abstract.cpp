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
        return (((addr.s_addr & 0xFF000000) >> 24 == 192 && (addr.s_addr & 0xFF0000) >> 16 == 168) ||
        		((addr.s_addr & 0xFF000000) >> 24 == 67 && (addr.s_addr & 0xFF0000) >> 16 == 194) ||
        		((addr.s_addr & 0xFF000000) >> 24 == 35 && (addr.s_addr & 0xFF0000) >> 16 == 0) ||
                (addr.s_addr & 0xFF000000) >> 24 == 10) ? true : false;

    //    return ((addr.s_addr & 0xFF) == 10) ? true : false;
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

void FlowAbstract::runMeasureTask(Result* result, Context& traceCtx, const struct pcap_pkthdr *header, const u_char *pkt_data) {
	/*
	 * first packet ever. set the base time.
	 * maintain the time of the last packet.
	 */
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

	/*
	 * update device context information
	 */
	traceCtx.updateContext(ts);

	/*
	 * Layer 3 (Network Layer) process
	 */
	if (*((u_short *)(pkt_data + ETHER_HDR_LEN - 2)) == ETHERTYPE_IP) {
		/*
		 * IP packet processing. Extract IP addresses and determine which one is the client IP
		 */
		ip_hdr = (ip *)(pkt_data + ETHER_HDR_LEN);
		// do swap to correct byte order
        bswapIP(ip_hdr);

		b1 = isClient(ip_hdr->ip_src);
		b2 = isClient(ip_hdr->ip_dst);
		int appIndex = -1;
		appIndex = *((u_short *)(pkt_data + 6)) & 0xFF;

		string appName("none");
		if (appIndex < traceCtx.getAppNameMap().size()) {
			appName.assign(traceCtx.getAppNameByIndex(appIndex));
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
			ignore_count1++;
		} else { //ignore 2, none are client IP
			ignore_count2++;
		}

		/*
		 * differentiate different users
		 */

		userp = &(users[traceCtx.getUserID()]);

		userp->userID.assign(traceCtx.getUserID());
		if (userp->start_time == 0) {
			//init
			userp->start_time = ts;
                        userp->cc_start = ts;
		}
		/* TCP Concurrency statistics*/
		if (ts - userp->cc_start > 1.0) {
			int concurrency = 0;
			for (uval_it = userp->tcp_flows.begin(); uval_it != userp->tcp_flows.end(); uval_it++) {
				if (uval_it->second->last_data_time > userp->cc_start)
					concurrency++;
			}
			if (concurrency > 0) {
				char buf[100];
				sprintf(buf, "%s %.6lf %d\n", traceCtx.getUserID().c_str(), userp->cc_start, concurrency);
				string s(buf);
				result->addResultToFile(1, s);
			}
			while (ts - userp->cc_start > 1.0)
				userp->cc_start += 1.0;
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
				} else if (traceType.compare(CONFIG_PARAM_TRACE_DEV)==0) {
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

					flow_index = port_clt * (((uint64)1) << 32) + ip_clt;
					flow_it_tmp = client_flows.find(flow_index);

					char buf[50];
					//sprintf(buf, "%.6f %" PRIu64 "", ts, flow_index);
					sprintf(buf, "%.6f", ts);

					if (flow_it_tmp != client_flows.end()) {
						flow = &(client_flows[flow_index]);
						//found flow
					//} else {
					} else if (flow_it_tmp == client_flows.end() && (tcp_hdr->syn) != 0 && (b1 && !b2)) {
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
					if ((tcp_hdr->fin) != 0 || (tcp_hdr->rst) != 0) {
						//flow->print((tcp_hdr->fin) | (tcp_hdr->rst));
						flow->last_data_ts = ts;
						//delete this flow
						userp->tcp_flows.erase(flow_index);
						client_flows.erase(flow_index);
						break;
					} else { // all packets of this flow goes to here except for the FIN and RST packets
						if (b1 && !b2) { // uplink
							if (payload_len > 0) {
								flow->last_data_time = ts;
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
							}

						} else if (!b1 && b2) { //downlink
							if (payload_len > 0) {
								flow->last_data_time = ts;
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
							}
						}
					}

					/*
					 * RTT and TCP pattern analysis
					 */
					if (b1 && !b2) { // uplink
                        flow->update_seq_x(tcp_hdr->seq, payload_len, ts);
					} else if (!b1 && b2) {
                        flow->window_size = flow->window_scale * tcp_hdr->window;
                        //cout << setprecision(16) << ts;
                        //cout << " " << flow->ConvertIPToString(ip_hdr->ip_src.s_addr);
                        //cout << " " << flow->ConvertIPToString(ip_hdr->ip_dst.s_addr);
                        //cout << " " << tcp_hdr->seq << " " << tcp_hdr->ack_seq << endl;
						flow->update_ack_x(tcp_hdr->ack_seq, payload_len, ts);
					}

					flow->last_data_ts = ts;
					userp->appTime[appName] = ts;
					/* end traceType == CONFIG_PARAM_TRACE_DEV */
			/*
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
                                		OutputFile::append(userp->http_req_stat, userp->http_req_stat_size, ts - userp->last_http_time, append_s, "http_stat_output_", traceCtx.getUserID());
                                		//cout << ">>>>>>>>>>>>>>>>>>>>> " << traceCtx.getUserID() << "\t" << (host+uri) << "\t" << (ts - userp->last_http_time)*1000.0 << endl;
                                	}
                                	userp->last_http_time = ts;

                                	//cout << ts << "\t" << appName << "\t" << host+uri << "\t" << method << endl;
                            	}
                                if (flow->user_agent.length() == 0) {
                                    //only record the first user agent
                                    start_pos = payload_str.find("User-Agent: ");
                                    end_pos = payload_str.find("\r\n", start_pos);
                                    if (start_pos != string::npos && end_pos > start_pos + 12)
                                        flow->user_agent = compress_user_agent(payload_str.substr(start_pos + 12, end_pos - start_pos - 12));
                                }

                                if (flow->host.length() == 0) {
                                    //only record the first user agent
                                    start_pos = payload_str.find("Host: ");
                                    end_pos = payload_str.find("\r\n", start_pos);
                                    if (start_pos != string::npos && end_pos > start_pos + 6)
                                        flow->host = payload_str.substr(start_pos + 6, end_pos - start_pos - 6);
                                }
                            } else if (appName.find("chrome", 0) >= 0 && appName.find("chrome", 0) < appName.length()) {
                            	userp->last_http_time = ts;
                            }
                        } else if (!b1 && b2) {
                            //DOWNLINK
                        	if (appName.find("chrome", 0) >= 0 && appName.find("chrome", 0) < appName.length()) {
                        		userp->last_http_time = ts;
                        	}
                            if (payload_str.find("HTTP/1.1 200 OK") == 0 || payload_str.find("HTTP/1.0 200 OK") == 0) {
                                //downlink HTTP 200 OK

                                if (flow->content_type.length() == 0) {
                                    //only record the first content type
                                    start_pos = payload_str.find("Content-Type: ");
                                    end_pos = payload_str.find("\r\n", start_pos);
                                    if (start_pos != string::npos && end_pos > start_pos + 14)
                                        flow->content_type = process_content_type(payload_str.substr(start_pos + 14, end_pos - start_pos - 14));
                                }

                                start_pos = payload_str.find("Content-Length: ");
                                end_pos = payload_str.find("\r\n", start_pos);
                                if (start_pos != string::npos && end_pos > start_pos + 16)
                                    flow->total_content_length += StringToNumber<int>(payload_str.substr(start_pos + 16, end_pos - start_pos - 16));

                            } else if (payload_str.find("HTTP/") == 0 && payload_str.find("200 OK") != -1) {
                                cout << "HTTP_RESPONSE_SPECIAL " << payload_str << endl;
                            }
                        }
                    }*/
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
