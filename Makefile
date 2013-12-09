CC=g++
CFLAGS=-I include/
LDFLAGS=-lpcap
LOCALLIB=/usr/local/lib/
LIBS=lib/
LIBFILE=libpcap.so.1.3.0
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

installlib: 
	cp $(LIBS)$(LIBFILE) $(LOCALLIB)
	ln -sf $(LOCALLIB)$(LIBFILE) $(LOCALLIB)libpcap.so.1
	ln -sf $(LOCALLIB)$(LIBFILE) $(LOCALLIB)libpcap.so
	export LD_LIBRARY_PATH=$(LOCALLIB):$LD_LIBRARY_PATH

$(EXECUTABLE):  installlib
	$(CC) $(OBJECTS) $(CFLAGS) -L$(LOCALLIB) -o $@ $(LDFLAGS)

.cpp.o:
	$(CC) -c $< $(CFLAGS) -o $@  

clean:
	rm -f $(EXECUTABLE) $(OBJECTS) *~
