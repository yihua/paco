#!/usr/bin/python
import c_session

flows = c_session.CFlow()
flows.load_data()

appname = "com.urbanairship.push.process"
for item in flows.data:
    if appname in item["app_name"]:
        print item["app_name"]
