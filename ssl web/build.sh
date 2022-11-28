#!/bin/bash
# mkdir -p build
g++ -Wall -std=c++11 -g -o server main.cpp SslServer.cpp -lcrypto -lssl
