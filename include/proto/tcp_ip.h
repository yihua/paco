/*
 * tcp_ip.h
 *
 *  Created on: Dec 8, 2013
 *      Author: yihua
 */

#ifndef TCPIP_H_
#define TCPIP_H_

#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>

#define ETHERTYPE_IP 0x08        /* IP protocol */

#define IP_HDR_LEN 20
#define UDP_HDR_LEN 8
#define BYTES_PER_32BIT_WORD 4

const int USEC_PER_SEC = 1000000;
const double FLOW_MAX_IDLE_TIME = 3600.0;
const double ONE_MILLION = 1000000.0;
const double GVAL_TIME = 3.0;
const double IDLE_THRESHOLD = 1.0; //seconds
const double DUPACK_SLOWSTART_TIME = 0.1; //seconds
#define TCP_MAX_PAYLOAD 1358

const double BW_MAX_BITS_PER_SECOND = 30000000.0;

//const int SEQ_INDEX_MAX = 1000;
//const int ACK_INDEX_MAX = SEQ_INDEX_MAX / 2; //1 ACK 2 Data PKTs

typedef struct {
    u_int src_ip;
    u_int dst_ip;
    u_short offset1;
    u_short offset2;
        u_short        ether_type;
} att_ether_hdr;

#endif /* TCPIP_H_ */
