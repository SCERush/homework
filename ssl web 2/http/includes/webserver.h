#ifndef WEBSERVER_H
#define WEBSERVER_H

#include "mytcp.h"
#include "http.h"
#include "global.h"
#include "sslsetting.h"

#define ALLOW_ACCEPT 1
#define HTTP_KIND int
#define HTTP 0
#define HTTPS 1

int RunWebServer(char *ip, int port, int maxListener, HTTP_KIND flag);
int RunHttpsServer(char *ip, int port, int maxListener);

#endif