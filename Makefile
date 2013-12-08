objects = main.o measure_task.o packet_analyzer.o param.o config_param.o

all: $(objects)
	g++ $(objects) -I include/ lib/libpcap.so.1.3.0 -o run

main.o: main.cpp
	g++ -c main.cpp -I include/

measure_task.o: framework/measure_task.cpp
	g++ -c framework/measure_task.cpp -I include/

packet_analyzer.o: framework/packet_analyzer.cpp 
	g++ -c framework/packet_analyzer.cpp -I include/

param.o: common/param.cpp
	g++ -c common/param.cpp -I include/

config_param.o: param/config_param.cpp
	g++ -c param/config_param.cpp -I include/
