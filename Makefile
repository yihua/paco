CC=g++
CFLAGS=-Wno-deprecated -g -I include/
LDFLAGS=-static -lpcap
LIBS=$(shell pwd)/lib
OBJECTS=$(SOURCES:.cpp=.o)
EXECUTABLE=paco

SOURCES=\
		main.cpp\
		framework/measure_task.cpp\
		framework/packet_analyzer.cpp\
		framework/user.cpp\
		framework/context.cpp\
		framework/result.cpp\
		common/param.cpp\
		common/output.cpp\
		param/config_param.cpp\
		abstract/tcp_flow.cpp\
		abstract/flow_abstract.cpp\
		abstract/packet_flow.cpp\
		abstract/packet.cpp\
		model/energy.cpp\
		framework/traffic_abstract.cpp\
		task/rtt_task.cpp\
		proto/http.cpp
		
Release: $(SOURCES) $(EXECUTABLE)
all: $(SOURCES) $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS)
	$(CC) $(OBJECTS) $(CFLAGS) -L$(LIBS) $(LDFLAGS) -o $@


.cpp.o:
	$(CC) -c $< $(CFLAGS) -o $@  

clean:
	rm -f $(EXECUTABLE) $(OBJECTS) *~
