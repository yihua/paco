/*
 * basic.h
 *
 *  Created on: Dec 6, 2013
 *      Author: yihua
 */

#ifndef _PACO_BASIC_H
#define _PACO_BASIC_H


#include <cstdlib>
#include <ctime>
#include <stdint.h>

typedef unsigned long long uint64;
#ifdef __FreeBSD__ || __NetBSD__ || __OpenBSD__
   #include <sys/endian.h>
   u_short bswap16(u_short);
   u_int bswap32(u_int);
#else
   #include <endian.h>
   #define bswap16(x) __bswap_16 (x)
   #define bswap32(x) __bswap_32 (x)
#endif

#endif /* _PACO_BASIC_H */
