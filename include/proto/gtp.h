/*
 * gtp.h
 *
 *  Created on: Nov 11, 2014
 *      Author: yihua
 */

#ifndef GTP_H_
#define GTP_H_

#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>

typedef struct {
#if BYTE_ORDER == LITTLE_ENDIAN
	uint16_t	pnb:1,
			seq:1,
			ext:1,
			res1:1,
			proto:1,
			ver:3,
			msg:8;
#elif BYTE_ORDER == BIG_ENDIAN
	uint16_t	ver:3,
			proto:1,
			res1:1,
			ext:1,
			seq:1,
			pnb:1,
			msg:8;
#endif
	uint16_t	len;
	uint32_t	teid;
} gtphdr;

#endif /* GTP_H_ */
