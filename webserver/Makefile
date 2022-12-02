CC=g++
CPPFLAGS=-g -w
LD=-lssl -lcrypto -ldl -lpthread

DIST=common.cpp \
	common.h \
	https.cpp \
	https.h \
	main.cpp \
	
WebServer: common.o main.o https.o
	$(CC) common.o main.o https.o -o WebServer $(LD)
	rm -r *.o

clean:	
	rm -r WebServer
