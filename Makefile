objects = main.o measure_task.o packet_analyzer.o param.o config_param.o tcp_flow.o traffic_abstract.o rtt_task.o

all: $(objects)
	g++ $(objects) -I include/ lib/libpcap.so.1.3.0 -o run

main.o: main.cpp
	g++ -c main.cpp -I include/

# abstract

flow_abstract.o: abstract/flow_abstract.cpp
	g++ -c abstract/flow_abstract.cpp -I include/

tcp_flow.o: abstract/tcp_flow.cpp
	g++ -c abstract/tcp_flow.cpp -I include/

# common

param.o: common/param.cpp
	g++ -c common/param.cpp -I include/

# framework

measure_task.o: framework/measure_task.cpp
	g++ -c framework/measure_task.cpp -I include/

packet_analyzer.o: framework/packet_analyzer.cpp 
	g++ -c framework/packet_analyzer.cpp -I include/

traffic_abstract.o: framework/traffic_abstract.cpp
	g++ -c framework/traffic_abstract.cpp -I include/

user.o: framework/user.cpp
	g++ -c framework/user.cpp -I include/

# param

config_param.o: param/config_param.cpp
	g++ -c param/config_param.cpp -I include/

# proto

tcp_ip.o: proto/tcp_ip.cpp
	g++ -c proto/tcp_ip.cpp -I include/

# task

rtt_task.o: task/rtt_task.cpp
	g++ -c task/rtt_task.cpp -I include/
