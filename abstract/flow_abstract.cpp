/*
 * flow_abstract.cpp
 *
 *  Created on: Dec 8, 2013
 *      Author: yihua
 */

#include "abstract/flow_abstract.h"

FlowAbstract::FlowAbstract() {
	is_first = true;
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
        return ((addr.s_addr & 0xFF) == 192 ||
                (addr.s_addr & 0xFF) == 198 ||
                (addr.s_addr & 0xFF) == 10 ||
                (addr.s_addr & 0xFF) == 32) ? true : false;

    //    return ((addr.s_addr & 0xFF) == 10) ? true : false;
}

void FlowAbstract::runMeasureTask(Context traceCtx, const struct pcap_pkthdr *header, const u_char *pkt_data) {
	if (is_first) {
		this->ETHER_HDR_LEN = traceCtx.getEtherLen();
		is_first = false;
		start_time_sec = header->ts.tv_sec;
		last_time_sec = start_time_sec;
		end_time_sec = start_time_sec;

		//if (RUNNING_LOCATION == RLOC_CONTROL_SERVER || RUNNING_LOCATION == RLOC_CONTROL_CLIENT) {
			TIME_BASE = (double)(header->ts.tv_sec) + (double)header->ts.tv_usec / (double)USEC_PER_SEC;
		//}
		cout << "TIME_BASE " << fixed << TIME_BASE << endl;
	} else {
		end_time_sec = header->ts.tv_sec;
	}

	ts = ((double)(header->ts.tv_sec) + (double)header->ts.tv_usec / (double)USEC_PER_SEC) - TIME_BASE;

	if (*((u_short *)(pkt_data + ETHER_HDR_LEN - 2)) == ETHERTYPE_IP) {
		//all IP
		pip = (ip *)(pkt_data + ETHER_HDR_LEN);
		b1 = isClient(pip->ip_src);
		b2 = isClient(pip->ip_dst);
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


		userp = &users[ip_clt];
		if (userp->start_time == 0) {
			//init
			userp->start_time = ts;
		}

		switch (pip->ip_p) {
			case IPPROTO_TCP:

				//break; //TODO only look at UDP now
				tcp_count++;
				ptcp = (tcphdr *)((u_char *)pip + BYTES_PER_32BIT_WORD * pip->ip_hl); //cast of u_char* is necessary
				payload_len = bswap16(pip->ip_len) - BYTES_PER_32BIT_WORD * (pip->ip_hl + ptcp->doff);

				opt_len = BYTES_PER_32BIT_WORD * ptcp->doff - 20;
				opt_ts = (u_int *)((u_char *)ptcp + 20);
				window_scale = 0;

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
				}

				if (traceType.compare("-1")==0) {
					//TCP client side throughput sampling
					/*if (b1 && !b2 && bw_tcp == NULL && (ptcp->th_flags & TH_SYN) != 0) {
						bw_tcp = new client_bw(ts, 1.0);
					}*/

					//BW estimation ground truth
					/*if (!b1 && b2) { //downlink
						//sample throughput here, using differnt time window
						bw_tcp->add_packet(payload_len, ts);
					}*/

					//G value ground truth
					/*if (b1 && !b2) { // uplink
						if ((ptcp->th_flags & TH_ACK) != 0) {
							opt_ts = (u_int *)((u_char *)ptcp + 24);
							if (double_start < 0) {
								u_int_start = bswap32(*opt_ts);
								double_start = ts;
							} else {
								cout << "G_GROUNDTRUTH " << (ts - double_start) / (bswap32(*opt_ts) - u_int_start) << endl;
							}
						}
					}//*/

					//analyze client trace to understand the delay between data and ack
					/*if (b1 && !b2) { // uplink
						if (ack_delay >= 0 && expected_ack == bswap32(ptcp->th_ack)) {
							cout << "ACK_DELAY " << ts - ack_delay << endl;
							ack_delay = -1;
						} else if (ack_delay >= 0 && expected_ack < bswap32(ptcp->th_ack)) {
							//abandon this sample
							ack_delay = -1;
						}
					} else if (!b1 && b2) { //downlink
						if (ack_delay < 0 && payload_len > 0) {
							ack_delay = ts;
							expected_ack = bswap32(ptcp->th_seq) + payload_len;
						}
					}*/
				/* end traceType == -1 */
				} else if (traceType.compare(CONFIG_PARAM_TRACE_DEV)==0) {
					if (b1 && !b2) { // uplink
						port_clt = bswap16(ptcp->source);
						port_svr = bswap16(ptcp->dest);

						tcp_up_bytes += payload_len;
						if (port_svr == 80 || port_svr == 8080) {
							http_up_bytes += payload_len;
						}
					} else if (!b1 && b2) { //downlink
						port_clt = bswap16(ptcp->dest);
						port_svr = bswap16(ptcp->source);

						tcp_down_bytes += payload_len;
						if (port_svr == 80 || port_svr == 8080) {
							http_down_bytes += payload_len;
						}
					} else {
						break;
					}

					/*//count CS IPs
					cip[ip_clt]++;
					sip[ip_svr]++;
					break;*/

					/*//dump concurrency results
					if (ts - last_sample_time > 100.0) {
						last_sample_time = ts;
						for (user_it = users.begin() ; user_it != users.end() ; user_it++) {
							//for each user
							int concurrency = 0;
							for (uval_it = (*user_it).second.tcp_flows.begin() ; uval_it != (*user_it).second.tcp_flows.end() ; uval_it++) {
								if (uval_it->second->last_byte_time > ts - 1.0)
									concurrency++;
							}
							if (concurrency > 0)
								printf("CC %.4lf %d\n", ts, concurrency);
						}
					}//*/

					//sequence number ACK number plot
					/*bool isUplink = true; //true for ACK, false for SEQ
					if (RUNNING_LOCATION == RLOC_CONTROL_SERVER) {
						if (b1 && !b2 && isUplink) { // uplink, for ack
							 cout << ts << " " << packet_count;
							 cout << " src " << ConvertIPToString(pip->ip_src.s_addr) << " ";
							 cout << " dst " << ConvertIPToString(pip->ip_dst.s_addr) << " ";
							 cout << bswap32(ptcp->th_ack) << endl;//
						} else if (!b1 && b2 && !isUplink) { //downlink, for seq
							cout << ts << " " << packet_count;
							cout << " src " << ConvertIPToString(pip->ip_src.s_addr) << " ";
							cout << " dst " << ConvertIPToString(pip->ip_dst.s_addr) << " ";
							cout << bswap32(ptcp->th_seq) << endl;//
						}
					}//*/

					/*//netflix study, this should be commented out for all other analysis
					//check whether current packet has TCP payload
					if (ETHER_HDR_LEN + BYTES_PER_32BIT_WORD * (pip->ip_hl + ptcp->th_off) < header->caplen)
						payload = (char *)((char *)ptcp + BYTES_PER_32BIT_WORD * ptcp->th_off);
					else
						payload = (char *)"";
					payload_str = string(payload);
					big_flow_index = ConvertIPToString(ip_clt) + string("_");
					big_flow_index += ConvertIPToString(ip_svr) + string("_");
					big_flow_index += NumberToString(port_clt) + string("_") + NumberToString(port_svr);
					if ((payload_str.find("GET ") == 0 || payload_str.find("HEAD ") == 0 ||
						payload_str.find("POST ") == 0 || payload_str.find("PUT ") == 0 ||
						payload_str.find("DELETE ") == 0 || payload_str.find("TRACE ") == 0 ||
						payload_str.find("OPTIONS ") == 0 || payload_str.find("CONNECT ") == 0 ||
						payload_str.find("PATCH ") == 0) && (b1 && !b2)) {
						//uplink HTTP request

						//output existing HTTP info
						if (big_flows[big_flow_index].first >= 0 && big_flows[big_flow_index].second > 0) {
							cout << big_flows[big_flow_index].first << " " << big_flows[big_flow_index].second;
							cout << " src " << ConvertIPToString(pip->ip_src.s_addr) << " ";
							cout << " dst " << ConvertIPToString(pip->ip_dst.s_addr) << " ";
							cout << port_clt << endl;
						}
						big_flows[big_flow_index] = make_pair(ts, 0);
					//} else if (payload_str.find("HTTP/1.") == 0 && (!b1 && b2)) {
						//downlink HTTP response
					//    size_t start_pos = payload_str.find("Content-Length: ");
					//    size_t end_pos = payload_str.find("\r\n", start_pos);
					//    int content_len = 0;
					//    if (start_pos != string::npos && end_pos > start_pos + 16)
					//        content_len = StringToNumber<int>(payload_str.substr(start_pos + 16, end_pos - start_pos - 16));
					} else if (payload_len > 0 && (!b1 && b2)) {
						big_flows[big_flow_index].second = ts;
					} else if ((ptcp->th_flags & TH_FIN) != 0 || (ptcp->th_flags & TH_RST) != 0) {
						//output existing HTTP info
						if (big_flows[big_flow_index].first >= 0 && big_flows[big_flow_index].second > 0) {
							cout << big_flows[big_flow_index].first << " " << big_flows[big_flow_index].second;
							cout << " src " << ConvertIPToString(pip->ip_src.s_addr) << " ";
							cout << " dst " << ConvertIPToString(pip->ip_dst.s_addr) << " ";
							cout << port_clt << endl;
						}
						big_flows[big_flow_index] = make_pair(-1, 0);
					}

					 //use UDP flow to calculate aggregate throughput
					 if (!b1 && b2) { //downlink
						//sample throughput here, using differnt time window
						if (bw_udp == NULL) {
							bw_udp = new client_bw(ts, 0.1);
						}
						bw_udp->add_packet(payload_len, ts);
					}//
					break;//*/

					//dump interested flow
					/*if (//big_flow_index.compare("10.134.12.177_96.17.164.36_1556_1935") == 0 ||
						//big_flow_index.compare("10.34.229.236_90.84.51.8_40214_80") == 0 ||
						//big_flow_index.compare("10.8.102.148_107.14.33.153_2463_80") == 0 ||
						//big_flow_index.compare("10.9.63.12_68.142.123.131_1216_80") == 0 ||
						//big_flow_index.compare("10.9.63.12_8.254.15.254_1504_80") == 0) {
						big_flow_index.compare("10.46.6.151_74.125.227.65_54587_80") == 0 //Youtube traffic, reusing flow
						//1231    180724  1350088578.551052       10.46.6.151     54587   74.125.227.65   80      Host: 3.bp.blogspot.com User-Agent: Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A403 Safari/8536.25        Referer: http://jenniferstano.blogspot.com/search?updated-max=2012-08-07T15:28:00-07:00&max-results=20&start=3&by-date=false    Http Len: 22746
						||
						 big_flow_index.compare("10.9.131.253_74.125.215.179_51071_80") == 0 //iPad, AppleCoreMedia
						//12601   1219331 1350876729.943984       10.9.131.253    51071   74.125.215.179  80      Host: r4---sn-a5m7zu7d.c.youtube.com    User-Agent: AppleCoreMedia/1.0.0.9B206 (iPad; U; CPU OS 5_1_1 like Mac OS X; en_us)     NULL    Http Len: 22747
						) {
						pcap_dump((u_char *)dumper, header, pkt_data);
						pcap_dump_flush(dumper);
					 }//*/

					//flow statistics analysis
					flow_index = port_clt * (((uint64)1) << 32) + ip_clt;
					flow_it_tmp = client_flows.find(flow_index);
					if (flow_it_tmp != client_flows.end()) {
						//found flow
					} else if (flow_it_tmp == client_flows.end() && (ptcp->syn) != 0 && (b1 && !b2)) {
						//no flow found, now uplink SYN packet

						/*//big flow analysis
						big_flow_index = ConvertIPToString(ip_clt) + string("_");
						big_flow_index += ConvertIPToString(ip_svr) + string("_");
						big_flow_index += NumberToString(port_clt) + string("_");
						big_flow_index += NumberToString(port_svr);

						big_flow_it_tmp = big_flows.find(big_flow_index);
						is_target_flow = false;
						if (big_flow_it_tmp != big_flows.end()) {
							//found big flow
							if (ts >= big_flows[big_flow_index].first && ts <= big_flows[big_flow_index].first + big_flows[big_flow_index].second) {
								//target flow found
								is_target_flow = true;
							}
						}
						if (!is_target_flow) {
							break;
						}
						//*/

						client_flows[flow_index].clt_ip = ip_clt; //init a flow
						flow_count++;

						flow = &client_flows[flow_index];
						userp->tcp_flows[port_clt] = flow;
						flow->idle_time_before_syn = ts - userp->last_packet_time;
						flow->svr_ip = ip_svr;
						flow->clt_port = port_clt;
						flow->svr_port = port_svr;
						flow->start_time = ts;
						flow->end_time = ts;

						if (traceType.compare(CONFIG_PARAM_TRACE_SRV)==0) {
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
										users[flow_it_tmp->second.clt_ip].tcp_flows.erase(flow_it_tmp->second.clt_port);
										client_flows.erase(flow_it_tmp);
									}
								}//*/
							}
						}//*/
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
						flow->print((ptcp->fin) | (ptcp->rst));
						//delete this flow
						userp->tcp_flows.erase(port_clt);
						client_flows.erase(flow_index);
						break;
					} else { // all packets of this flow goes to here except for the FIN and RST packets
						if (b1 && !b2) { // uplink
							if (payload_len > 0) {
								flow->total_up_payloads += payload_len;
							}
							if (opt_len == 100) {
								//there is TCP timestamp options
								flow->has_ts_option_clt = true;

								if (flow->packet_count == 1 && (ptcp->syn) != 0) {
									//SYN
									flow->promotion_delay = -1 * bswap32(*opt_ts);
									flow->window_scale = window_scale;
								} else if (flow->packet_count == 3 && (ptcp->syn) == 0 && flow->promotion_delay < 0) {
									//this is not a repeated SYN
									//ACK 3
									flow->promotion_delay += bswap32(*opt_ts);
									flow->window_initial_size = flow->window_scale * bswap16(ptcp->window);
								}
							}
						} else if (!b1 && b2) { //downlink
							if (payload_len > 0) {
								flow->total_down_payloads += payload_len;
								flow->last_byte_time = ts;
								if (flow->first_byte_time == 0) {
									flow->first_byte_time = ts;
								}
							}
							if (opt_len == 100) //there is TCP timestamp options
								flow->has_ts_option_svr = true;
						}
					}


					//RTT and TCP pattern analysis
					if (ip_clt == flow->clt_ip &&
						ip_svr == flow->svr_ip &&
						port_clt == flow->clt_port &&
						port_svr == flow->svr_port) {
						if (b1 && !b2) { // uplink
							flow->window_size = flow->window_scale * bswap16(ptcp->window); //only update receiver's window
							flow->update_ack_x(bswap32(ptcp->ack_seq), payload_len, ts);
						} else if (!b1 && b2) { //downlink
							flow->update_seq_x(bswap32(ptcp->seq), payload_len, ts);
						}
						//cout << "EMPTY_WINDOW " << ts << " " << flow->window_size - flow->bytes_in_fly << endl;
						//sample bytes_in_fly
						//if ((SAMPLES++) % SAMPLE_CYCLE == 0)
						//    cout << "BF " << flow->bytes_in_fly << endl;

					}//*/

					//HTTP analysis
					/*if (ETHER_HDR_LEN + BYTES_PER_32BIT_WORD * (pip->ip_hl + ptcp->th_off) < header->caplen) {
						//has TCP payload
						payload = (char *)((char *)ptcp + BYTES_PER_32BIT_WORD * ptcp->th_off);
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
							}
						} else if (!b1 && b2) {
							//DOWNLINK
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

							//} else if (payload_str.find("HTTP/") == 0 && payload_str.find("200 OK") != -1) {
							//    cout << "HTTP_RESPONSE_SPECIAL " << payload_str << endl;
							}
						}
					}//*/

					//BWE analysis, the first part can be used for G inference only
					if (flow->gval < 0) {
						//do G inference for BW estimate
						if (b1 && !b2) { // uplink
							if ((ptcp->ack) != 0) {
								if (opt_len == 100) {
									if (flow->double_start < 0) {
										flow->u_int_start = bswap32(*opt_ts);
										flow->double_start = ts;
										//cout << "TCP header length of the first uplink ACK " << BYTES_PER_32BIT_WORD * ptcp->th_off << endl;
									} else if (flow->double_start > 0 && ts - flow->double_start > GVAL_TIME) {
										flow->gval = (ts - flow->double_start) / (bswap32(*opt_ts) - flow->u_int_start);
										//cout << "G_INFER " << " t_off " << (ts - flow->double_start) << " G: " << flow->gval << " s/tick" << endl;
									}
								}
							}
						}
					}/* else {
						//do BW estimation
						if (ip_clt == flow->clt_ip && ip_svr == flow->svr_ip &&
							port_clt == flow->clt_port && port_svr == flow->svr_port) {
							if (b1 && !b2) { // uplink
								if ((ptcp->th_flags & TH_ACK) != 0) {
									flow->update_ack(bswap32(ptcp->th_ack), payload_len, flow->gval * bswap32(*opt_ts), ts);
								}
							} else if (!b1 && b2) { //downlink
								//payload_len > < 0 check inside update_seq
								flow->update_seq(bswap32(ptcp->th_seq), payload_len, ts);
							}
						}
					}//*/

					/*//G inference
					if (RUNNING_LOCATION == RLOC_CONTROL_SERVER) {
						if (b1 && !b2) { // uplink
							if ((ptcp->th_flags & TH_ACK) != 0) {
								if (flow->double_start < 0 && ts > 100) {
									flow->u_int_start = bswap32(*opt_ts);
									flow->double_start = ts;
								} else if (flow->double_start > 0) {
									flow->gval = (ts - flow->double_start) / (bswap32(*opt_ts) - flow->u_int_start);
									if (packet_count % 3 == 0)
										cout << "G_INFERENCE " << (ts - flow->double_start) << " " << flow->gval << endl;
								}
							}
						}
					}//*/


					/*if (packet_count == 38084) {
						cout << "create flow here" << endl;
						flow = new tcp_flow(ip_svr, ip_clt, port_svr, port_clt);
					}
					if (packet_count >= 38084) {
						//flow is not null
						if (ip_clt == flow->clt_ip &&
							ip_svr == flow->svr_ip &&
							port_clt == flow->clt_port &&
							port_svr == flow->svr_port) {
							if (b1 && !b2) { // uplink
								//cout << "target uplink packet " << packet_count << endl;
								//target flow, ack packets
								if (bswap32(ptcp->th_ack) > 0) {
									flow->update_ack(bswap32(ptcp->th_ack), ts);
								}
							} else if (!b1 && b2) { //downlink
								//cout << "target downlink packet " << packet_count << endl;
								//target flow
								if (payload_len >= TCP_MAX_PAYLOAD) {
									flow->update_seq(bswap32(ptcp->th_seq), payload_len, ts);
								}
							}
						}
					}//*/
					/* end traceType == CONFIG_PARAM_TRACE_DEV */
				}

				break;
			case IPPROTO_UDP:
				udp_count++;
				pudp = (udphdr *)((u_char *)pip + sizeof(ip));
				payload_len = bswap16(pudp->len) - UDP_HDR_LEN;

				if (b1 && !b2) { // uplink
					ip_clt = pip->ip_src.s_addr;
					ip_svr = pip->ip_dst.s_addr;
					udp_up_bytes += payload_len;
				} else if (!b1 && b2) { //downlink
					ip_clt = pip->ip_dst.s_addr;
					ip_svr = pip->ip_src.s_addr;
					udp_down_bytes += payload_len;
				} else {
					break;
				}
				/*//count CS IPs
				cip[ip_clt]++;
				sip[ip_svr]++;*/

				if (traceType.compare("-1")==0) {
					//UDP client side throughput sampling
					if (!b1 && b2) { //downlink
						//sample throughput here, using differnt time window
						/*if (bw_udp == NULL) {
							bw_udp = new client_bw(ts, 0.5);
						}
						bw_udp->add_packet(payload_len, ts);*/
					}
				}
				/*//DNS analysis
				if (b1 && !b2) { // uplink
					ip_clt = pip->ip_src.s_addr;
					ip_svr = pip->ip_dst.s_addr;
					port_clt = bswap16(pudp->uh_sport);
					port_svr = bswap16(pudp->uh_dport);
				} else if (!b1 && b2) { //downlink
					ip_clt = pip->ip_dst.s_addr;
					ip_svr = pip->ip_src.s_addr;
					port_clt = bswap16(pudp->uh_dport);
					port_svr = bswap16(pudp->uh_sport);
				} else {
					break;
				}

				if (port_svr == 53) {
					//UDP flow statistics analysis
					flow_index = port_clt * (((uint64)1) << 32) + ip_clt;
					flow_it_tmp = client_flows.find(flow_index);
					if (flow_it_tmp != client_flows.end()) {
						//found flow
					} else if (flow_it_tmp == client_flows.end() && (b1 && !b2)) {
						client_flows[flow_index].clt_ip = ip_clt;
						flow_count++;

						flow = &client_flows[flow_index];
						flow->svr_ip = ip_svr;
						flow->clt_port = port_clt;
						flow->svr_port = port_svr;
						flow->start_time = ts;
						flow->end_time = ts;

						if (RUNNING_LOCATION == RLOC_ATT_SERVER) {
							if (client_flows.size() >= 100000 && ts - last_prune_time >= FLOW_MAX_IDLE_TIME / 2) {
								//if (ts - last_prune_time >= FLOW_MAX_IDLE_TIME) {
								cout << "Flowsize " << ts << " " << client_flows.size() << endl;
								last_prune_time = ts; //only prune once for every 100 seconds
								for (flow_it = client_flows.begin() ; flow_it != client_flows.end() ; ) {
									flow_it_tmp = flow_it;
									flow_it++;
									if (flow_it_tmp->second.end_time < ts - FLOW_MAX_IDLE_TIME)
										client_flows.erase(flow_it_tmp);
								}//
							}
						}//
					} else {
						break;
					}

					flow = &client_flows[flow_index];
					if (b1 && !b2) { // uplink
						flow->end_time = ts;
					} else if (!b1 && b2) { //downlink
						cout << "D " << ConvertIPToString(flow->svr_ip) << " " << (ts - flow->end_time) << endl;
						client_flows.erase(flow_index);
					}
				}//*/

				//cout << "UDP src port " << bswap16(pudp->uh_sport) << " dst port " << bswap16(pudp->uh_dport) << endl;
				break;
			case IPPROTO_ICMP:
				icmp_count++;
				break;
			default:
				break;
		}

		//everything is in IP

		if (userp->last_packet_time > 0 && ts > userp->last_packet_time + 1.0) {
			//printf("UI %.4lf\n", ts - userp->last_packet_time);
		}
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
