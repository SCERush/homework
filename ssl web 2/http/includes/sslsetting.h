#ifndef SSL_H
#define SSL_H

#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/rand.h>

#include "global.h"

#define CERTF "SSL/server/server.crt"
#define KEYF "SSL/server/server.key"
#define CAFILE "SSL/ca/root.crt"

SSL_CTX *InitSSL();
SSL *AttachSSLWithSocket(int sockId, SSL_CTX *ctx);
Bool VerifyX509(SSL *ssl);
void FreeSSL(SSL *ssl, SSL_CTX *ctx);

#endif