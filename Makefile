CC=g++
CFLAGS=-I include/
LIBS=lib/libpcap.so.1.3.0
OBJECTS=$(SOURCES:.cpp=.o)
EXECUTABLE=paco

SOURCES=\
		main.cpp\
		framework/measure_task.cpp\
		framework/packet_analyzer.cpp\
		common/param.cpp\
		param/config_param.cpp\
		abstract/tcp_flow.cpp\
		framework/traffic_abstract.cpp\
		task/rtt_task.cpp
		


		

all: $(OBJECTS) $(EXECUTABLE)

$(EXECUTABLE):  
	$(CC) $(OBJECTS) $(CFLAGS) $(LIBS)  -o $@ 

.cpp.o:
	$(CC) -c $< $(CFLAGS) -o $@  

clean:
	rm -f $(EXECUTABLE) $(OBJECTS) *~
