/*
 * http.cpp
 *
 *  Created on: Feb 11, 2013
 *      Author: yihua
 */


#include "proto/http.h"

string compress_user_agent(string ua) {
    string::iterator it, it_tmp;
    for (it = ua.begin() ; it < ua.end() ; ) {
        if ((*it >= 'a' && *it <= 'z') || (*it >= 'A' && *it <= 'Z')) {
            it++;
        } else {
            it_tmp = it;
            it++;
            ua.erase(it_tmp);
            it--;
        }
    }
    return ua;
}

string process_content_type(string str) {
    string::iterator it, it_tmp;
    for (it = str.begin() ; it < str.end() ; ) {
        if (*it >= 'A' && *it <= 'Z') {
            *it = (char)((*it) - 'A' + 'a'); //to lower case
        } else if (*it == ' ') {
            str.erase(it++);
            continue;
        }

        if (*it == ';') {
            str.erase(it, str.end());
            break;
        }
        it++;
    }
    return str;
}

string trim_string(string str) {
    string::iterator it;
    for (it = str.begin() ; it < str.end() ; ) {
        if (*it == '\r' || *it == '\n') {
            str.erase(it, str.end());
            break;
        }

        if (*it == ' ') {
            str.erase(it++);
            continue;
        }
        it++;
    }
    return str;
}