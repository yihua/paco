CC=g++
CFLAGS=-Wno-deprecated -I include/
LDFLAGS=-static -lpcap
LIBS=$(shell pwd)/lib
OBJECTS=$(SOURCES:.cpp=.o)
EXECUTABLE=paco

SOURCES=\
		main.cpp\
		framework/measure_task.cpp\
		framework/packet_analyzer.cpp\
		framework/context.cpp\
		common/param.cpp\
		param/config_param.cpp\
		abstract/tcp_flow.cpp\
		framework/traffic_abstract.cpp\
		task/rtt_task.cpp
		


		

all: $(OBJECTS) $(EXECUTABLE)

$(EXECUTABLE):  
	$(CC) $(OBJECTS) $(CFLAGS) -L$(LIBS) $(LDFLAGS) -o $@


.cpp.o:
	$(CC) -c $< $(CFLAGS) -o $@  

clean:
	rm -f $(EXECUTABLE) $(OBJECTS) *~
