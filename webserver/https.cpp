#include <sys/stat.h>

#include "common.h"
#include "https.h"

char *CHttps::pass = PASSWORD;

CHttps::CHttps(void)
{
    bio_err = 0;
    // m_strRootDir = "./www/html"; //需修改此路径
    ErrorMsg = "";
    //创建上下文环境
    ErrorMsg = initialize_ctx();
    if (ErrorMsg == "")
    {
        ErrorMsg = load_dh_params(ctx, ROOTKEYPEM);
    }
    else
        printf("%s \n", ErrorMsg);
}

CHttps::~CHttps(void)
{
    // 释放SSL上下文环境
    SSL_CTX_free(ctx);
}

char *CHttps::initialize_ctx()
{
    const SSL_METHOD *meth;

    if (!bio_err)
    {
        //初始化OpenSSL库,加载OpenSSL将会用到的算法
        SSL_library_init();
        // 加载错误字符串
        SSL_load_error_strings();
        // An error write context
        bio_err = BIO_new_fp(stderr, BIO_NOCLOSE);
    }
    else
    {
        return "initialize_ctx() error!";
    }

    // Create our context
    meth = SSLv23_method();
    ctx = SSL_CTX_new(meth);

    // 指定所使用的证书文件
    if (!(SSL_CTX_use_certificate_chain_file(ctx, SERVERPEM)))
    {
        char *Str = "SSL_CTX_use_certificate_chain_file error!";
        return Str;
    }

    // 设置密码回调函数
    SSL_CTX_set_default_passwd_cb(ctx, password_cb);

    // 加载私钥文件
    if (!(SSL_CTX_use_PrivateKey_file(ctx, SERVERKEYPEM, SSL_FILETYPE_PEM)))
    {
        char *Str = "SSL_CTX_use_PrivateKey_file error!";
        return Str;
    }

    // 加载受信任的CA证书
    if (!(SSL_CTX_load_verify_locations(ctx, ROOTCERTPEM, 0)))
    {
        char *Str = "SSL_CTX_load_verify_locations error!";
        return Str;
    }
    return "";
}

char *CHttps::load_dh_params(SSL_CTX *ctx, char *file)
{
    DH *ret = 0;
    BIO *bio;

    if ((bio = BIO_new_file(file, "r")) == NULL)
    {
        char *Str = "BIO_new_file error!";
        return Str;
    }

    ret = PEM_read_bio_DHparams(bio, NULL, NULL, NULL);
    BIO_free(bio);
    if (SSL_CTX_set_tmp_dh(ctx, ret) < 0)
    {
        char *Str = "SSL_CTX_set_tmp_dh error!";
        return Str;
    }
    return "";
}

int CHttps::password_cb(char *buf, int num, int rwflag, void *userdata)
{
    if ((unsigned int)num < strlen(pass) + 1)
    {
        return (0);
    }

    strcpy(buf, pass);
    return (strlen(pass));
}

void CHttps::err_exit(char *str)
{
    printf("%s \n", str);
    // exit(1);
}

void CHttps::Disconnect(PREQUEST pReq)
{
    // 关闭套接字：释放所占有的资源
    int nRet;
    printf("Closing socket! \r\n\n");

    nRet = close(pReq->Socket);
    if (nRet == SOCKET_ERROR)
    {
        printf("Closing socket error! \r\n");
    }
}

void CHttps::CreateTypeMap()
{
    // 初始化map
    m_typeMap[".docx"] = "application/msword";
    m_typeMap[".bin"] = "application/octet-stream";
    m_typeMap[".dll"] = "application/octet-stream";
    m_typeMap[".exe"] = "application/octet-stream";
    m_typeMap[".pdf"] = "application/pdf";
    m_typeMap[".ai"] = "application/postscript";
    m_typeMap[".eps"] = "application/postscript";
    m_typeMap[".ps"] = "application/postscript";
    m_typeMap[".rtf"] = "application/rtf";
    m_typeMap[".fdf"] = "application/vnd.fdf";
    m_typeMap[".arj"] = "application/x-arj";
    m_typeMap[".gz"] = "application/x-gzip";
    m_typeMap[".class"] = "application/x-java-class";
    m_typeMap[".js"] = "application/x-javascript";
    m_typeMap[".lzh"] = "application/x-lzh";
    m_typeMap[".lnk"] = "application/x-ms-shortcut";
    m_typeMap[".tar"] = "application/x-tar";
    m_typeMap[".hlp"] = "application/x-winhelp";
    m_typeMap[".cert"] = "application/x-x509-ca-cert";
    m_typeMap[".zip"] = "application/zip";
    m_typeMap[".cab"] = "application/x-compressed";
    m_typeMap[".arj"] = "application/x-compressed";
    m_typeMap[".aif"] = "audio/aiff";
    m_typeMap[".aifc"] = "audio/aiff";
    m_typeMap[".aiff"] = "audio/aiff";
    m_typeMap[".au"] = "audio/basic";
    m_typeMap[".snd"] = "audio/basic";
    m_typeMap[".mid"] = "audio/midi";
    m_typeMap[".rmi"] = "audio/midi";
    m_typeMap[".mp3"] = "audio/mpeg";
    m_typeMap[".vox"] = "audio/voxware";
    m_typeMap[".wav"] = "audio/wav";
    m_typeMap[".ra"] = "audio/x-pn-realaudio";
    m_typeMap[".ram"] = "audio/x-pn-realaudio";
    m_typeMap[".bmp"] = "image/bmp";
    m_typeMap[".gif"] = "image/gif";
    m_typeMap[".jpeg"] = "image/jpeg";
    m_typeMap[".jpg"] = "image/jpeg";
    m_typeMap[".tif"] = "image/tiff";
    m_typeMap[".tiff"] = "image/tiff";
    m_typeMap[".xbm"] = "image/xbm";
    m_typeMap[".wrl"] = "model/vrml";
    m_typeMap[".htm"] = "text/html";
    m_typeMap[".html"] = "text/html";
    m_typeMap[".c"] = "text/plain";
    m_typeMap[".cpp"] = "text/plain";
    m_typeMap[".def"] = "text/plain";
    m_typeMap[".h"] = "text/plain";
    m_typeMap[".txt"] = "text/plain";
    m_typeMap[".rtx"] = "text/richtext";
    m_typeMap[".rtf"] = "text/richtext";
    m_typeMap[".java"] = "text/x-java-source";
    m_typeMap[".css"] = "text/css";
    m_typeMap[".mpeg"] = "video/mpeg";
    m_typeMap[".mpg"] = "video/mpeg";
    m_typeMap[".mpe"] = "video/mpeg";
    m_typeMap[".avi"] = "video/msvideo";
    m_typeMap[".mov"] = "video/quicktime";
    m_typeMap[".qt"] = "video/quicktime";
    m_typeMap[".shtml"] = "wwwserver/html-ssi";
    m_typeMap[".asa"] = "wwwserver/isapi";
    m_typeMap[".asp"] = "wwwserver/isapi";
    m_typeMap[".cfm"] = "wwwserver/isapi";
    m_typeMap[".dbm"] = "wwwserver/isapi";
    m_typeMap[".isa"] = "wwwserver/isapi";
    m_typeMap[".plx"] = "wwwserver/isapi";
    m_typeMap[".url"] = "wwwserver/isapi";
    m_typeMap[".cgi"] = "wwwserver/isapi";
    m_typeMap[".php"] = "wwwserver/isapi";
    m_typeMap[".wcgi"] = "wwwserver/isapi";
}

int CHttps::TcpListen()
{
    int sock;
    struct sockaddr_in sin;

    if ((sock = socket(PF_INET, SOCK_STREAM, 0)) < 0) //设置套接字协议族等信息
        err_exit("Couldn't make socket");

    memset(&sin, 0, sizeof(sin));
    sin.sin_addr.s_addr = INADDR_ANY;
    sin.sin_family = PF_INET;
    sin.sin_port = htons(HTTPSPORT); //访问端口

    const int trueFlag = 1;
    setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &trueFlag, sizeof(int));

    if (bind(sock, (struct sockaddr *)&sin, sizeof(struct sockaddr)) < 0) //命名套接字
    {
        printf("socket bind error = %d\n", errno);
        err_exit("Couldn't bind");
    }
    listen(sock, 5); //设置队列

    return sock;
}

bool CHttps::SSLRecvRequest(SSL *ssl, BIO *io, LPBYTE pBuf, DWORD dwBufSize, string &body)
{
    char buf[BUFSIZZ];
    int r, length = 0;

    memset(buf, 0, BUFSIZZ); //初始化缓冲区
    while (1)
    {
        r = BIO_gets(io, buf, BUFSIZZ - 1);
        switch (SSL_get_error(ssl, r))
        {
        case SSL_ERROR_NONE:
            memcpy(&pBuf[length], buf, r);
            length += r;
            break;
        default:
            break;
        }
        // 直到读到代表HTTP头部结束的空行
        if (!strcmp(buf, "\r\n") || !strcmp(buf, "\n"))
            break;
    }
    // 添加结束符
    pBuf[length] = '\0';

    string header = string((char *)pBuf);
    body = string();
    smatch result;
    regex pattern("Content-Length: (\\d+)");
    string::const_iterator itStart = header.begin();
    string::const_iterator itEnd = header.end();
    if (regex_search(itStart, itEnd, result, pattern))
    {
        int content_length = stoi(result[1]);
        printf("Content-Length = %d\n", content_length);
        if (content_length > 0)
        {
            memset(buf, 0, BUFSIZZ); //初始化缓冲区
            r = BIO_read(io, buf, content_length);
            switch (SSL_get_error(ssl, r))
            {
            case SSL_ERROR_NONE:
                body += string(buf);
                printf(">>>%s<<<\n", buf);
                break;
            default:
                break;
            }
        }
    }
    return true;
}

bool CHttps::StartHttpSrv()
{
    CreateTypeMap();

    printf("*******************Server starts************************ \n");

    pid_t pid;
    m_listenSocket = TcpListen(); //设置监听线程，负责处理请求

    pthread_t listen_tid;
    pthread_create(&listen_tid, NULL, &ListenThread, this);
}

void *CHttps::ListenThread(LPVOID param)
{
    printf("Starting ListenThread... \n");

    CHttps *pHttps = (CHttps *)param;

    SOCKET socketClient;
    pthread_t client_tid;
    struct sockaddr_in SockAddr;
    PREQUEST pReq;
    socklen_t nLen;
    DWORD dwRet;

    while (1) // 循环等待,如有客户连接请求,则接受客户机连接要求
    {
        nLen = sizeof(SockAddr);
        // 套接字等待链接,返回对应已接受的客户机连接的套接字
        socketClient = accept(pHttps->m_listenSocket, (LPSOCKADDR)&SockAddr, &nLen);
        // printf("%s ",inet_ntoa(SockAddr.sin_addr));
        if (socketClient == INVALID_SOCKET)
        {
            printf("INVALID_SOCKET !\n");
            break;
        }
        pReq = new REQUEST;
        pReq->Socket = socketClient;
        pReq->hFile = -1;
        pReq->dwRecv = 0;
        pReq->dwSend = 0;
        pReq->pHttps = pHttps;
        pReq->ssl_ctx = pHttps->ctx;

        // 创建client进程，处理request
        // printf("New request");
        pthread_create(&client_tid, NULL, &ClientThread, pReq);
    } // while

    return NULL;
}

void *CHttps::ClientThread(LPVOID param)
{
    printf("Starting ClientThread... \n");
    int nRet;
    SSL *ssl;
    BYTE buf[4096];
    BIO *sbio, *io, *ssl_bio;
    PREQUEST pReq = (PREQUEST)param;
    CHttps *pHttps = (CHttps *)pReq->pHttps;
    SOCKET s = pReq->Socket;

    sbio = BIO_new_socket(s, BIO_NOCLOSE); // 创建一个socket类型的BIO对象
    ssl = SSL_new(pReq->ssl_ctx);          // 创建一个SSL对象
    SSL_set_bio(ssl, sbio, sbio);          // 把SSL对象绑定到socket类型的BIO上
    nRet = SSL_accept(ssl);                // 连接客户端，在SSL_accept过程中，将会占用很大的cpu
    // nRet<=0时发生错误
    if (nRet <= 0)
    {
        printf("SSL ERROR = %d\n", SSL_get_error(ssl, nRet));
        pHttps->Disconnect(pReq);
        pHttps->err_exit("SSL_accept()error! \r\n");
    }

    io = BIO_new(BIO_f_buffer());         // 封装了缓冲区操作的BIO，写入该接口的数据一般是准备传入下一个BIO接口的，从该接口读出的数据一般也是从另一个BIO传过来的。
    ssl_bio = BIO_new(BIO_f_ssl());       // 封装了openssl 的SSL协议的BIO类型，也就是为SSL协议增加了一些BIO操作方法。
    BIO_set_ssl(ssl_bio, ssl, BIO_CLOSE); // 把ssl(SSL对象)封装在ssl_bio(SSL_BIO对象)中把ssl_bio封装在一个缓冲的BIO对象中，这种方法允许
    BIO_push(io, ssl_bio);                // 我们使用BIO_*函数族来操作新类型的IO对象,从而实现对SSL连接的缓冲读和写

    // 接收request data
    printf("********************************************************\r\n");
    string body;
    if (!pHttps->SSLRecvRequest(ssl, io, buf, sizeof(buf), body))
    {
        // 处理错误
        pHttps->Disconnect(pReq);
        pHttps->err_exit("Receiving SSLRequest error!! \r\n");
    }
    else
    {
        printf("[Request]\t\n");
        printf("%s \n", buf);
    }

    string method; // 请求的方法名
    str2str args;  // 请求的参数
    nRet = pHttps->Analyze(pReq, buf, body, method, args);
    // printf("Analyze Result:\n\tMethod = %d\n\tmethod = %s\n\tbody = %s\n", pReq->nMethod, method.c_str(), body.c_str());
    printMap(args);

    if (nRet)
    {
        // 处理错误
        pHttps->Disconnect(pReq);
        delete pReq;
        pHttps->err_exit("Analyzing request from client error!!\r\n");
    }

    // 生成并返回头部
    if (!pHttps->SSLSendHeader(pReq, io, method))
    {
        pHttps->Disconnect(pReq);
        pHttps->err_exit("Sending fileheader error!\r\n");
    }
    BIO_flush(io);

    // 向client传送数据
    if (pReq->nMethod == METHOD_GET)
    {
        if (method == groupGenToken)
        {
            pHttps->_groupGenToken_response(args);
            pHttps->SSLSendJson(pReq, io);
        }
        else if (method == recvText)
        {
            pHttps->_recvText_response(args);
            pHttps->SSLSendJson(pReq, io);
        }
        else
        {
            if (!pHttps->SSLSendFile(pReq, io))
                return 0;
        }
    }
    else if (pReq->nMethod == METHOD_POST)
    {
        if (method == groupUseToken)
        {
            pHttps->_groupUseToken_response(args);
            pHttps->SSLSendJson(pReq, io);
        }
        else if (method == sendText)
        {
            pHttps->_sendText_response(args);
            pHttps->SSLSendJson(pReq, io);
        }
    }
    pHttps->Disconnect(pReq);
    delete pReq;
    SSL_free(ssl);
    return NULL;
}

int CHttps::Analyze(PREQUEST pReq, LPBYTE pBuf, string &body, string &method, str2str &args)
{
    // 分析接收到的信息
    char szSeps[] = " \n";
    char *cpToken;
    // 防止非法请求
    if (strstr((const char *)pBuf, "..") != NULL)
    {
        strcpy(pReq->StatuCodeReason, HTTP_STATUS_BADREQUEST);
        return 1;
    }

    // 判断ruquest的mothed
    cpToken = strtok((char *)pBuf, szSeps); // 缓存中字符串分解为一组标记串。
    // printf("%s\n", cpToken);
    if (!strcmp(cpToken, "GET")) // GET命令
    {
        pReq->nMethod = METHOD_GET;
    }
    else if (!strcmp(cpToken, "HEAD")) // HEAD命令
    {
        pReq->nMethod = METHOD_HEAD;
    }
    else if (!strcmp(cpToken, "POST")) // POST命令
    {
        pReq->nMethod = METHOD_POST;
    }
    else
    {
        strcpy(pReq->StatuCodeReason, HTTP_STATUS_NOTIMPLEMENTED);
        return 1;
    }

    // 获取Request-URI
    cpToken = strtok(NULL, szSeps);
    if (cpToken == NULL)
    {
        strcpy(pReq->StatuCodeReason, HTTP_STATUS_BADREQUEST);
        return 1;
    }

    string methodArgs = string(cpToken);
    char *methodToken = strtok(cpToken, "?");
    method = string(methodToken);

    args.clear();
    smatch result;
    regex pattern("(\\?|\\&)([^=]+)\\=([^&]+)");
    string::const_iterator itStart = methodArgs.begin();
    string::const_iterator itEnd = methodArgs.end();
    while (regex_search(itStart, itEnd, result, pattern))
    {
        args[result[2]] = result[3];
        itStart = result[0].second;
    }
    pattern = regex("(\\&)?([^=]+)\\=([^&]+)");
    itStart = body.begin();
    itEnd = body.end();
    while (regex_search(itStart, itEnd, result, pattern))
    {
        args[result[2]] = result[3];
        itStart = result[0].second;
    }

    strcpy(pReq->szFileName, m_strRootDir);
    if (strlen(cpToken) > 1)
    {
        strcat(pReq->szFileName, cpToken); // 把该文件名添加到结尾处形成路径
    }
    else
    {
        strcat(pReq->szFileName, "/index.html");
    }

    return 0;
}

int CHttps::FileExist(PREQUEST pReq)
{
    pReq->hFile = open(pReq->szFileName, O_RDONLY);
    // 如果文件不存在，则返回出错信息
    if (pReq->hFile == -1)
    {
        strcpy(pReq->StatuCodeReason, HTTP_STATUS_NOTFOUND);
        printf("open %s error\n", pReq->szFileName);
        strcpy(pReq->szFileName, m_str404html);
        pReq->hFile = open(pReq->szFileName, O_RDONLY);
        return 1;
    }
    else
    {
        return 1;
    }
}

void CHttps::Test(PREQUEST pReq)
{
    struct stat buf;
    long fl;
    if (stat(pReq->szFileName, &buf) < 0)
    {
        Disconnect(pReq);
        err_exit("Getting filesize error!!\r\n");
    }
    fl = buf.st_size;
    printf("Filesize = %ld \r\n", fl);
}

void CHttps::GetCurrentTime(LPSTR lpszString)
{
    // 格林威治时间的星期转换
    char *week[] = {
        "Sun,",
        "Mon,",
        "Tue,",
        "Wed,",
        "Thu,",
        "Fri,",
        "Sat,",
    };
    // 格林威治时间的月份转换
    char *month[] = {
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    };
    // 活动本地时间
    struct tm *st;
    long ct;
    ct = time(&ct);
    st = (struct tm *)localtime(&ct);
    // 时间格式化
    sprintf(lpszString,
            "%s %02d %s %d %02d:%02d:%02d GMT",
            week[st->tm_wday],
            st->tm_mday,
            month[st->tm_mon],
            1900 + st->tm_year,
            st->tm_hour,
            st->tm_min,
            st->tm_sec);
}

bool CHttps::GetContentType(PREQUEST pReq, LPSTR type)
{
    // 取得文件的类型
    char *cpToken;
    cpToken = strstr(pReq->szFileName, ".");
    strcpy(pReq->postfix, cpToken);
    // 遍历搜索该文件类型对应的content-type
    // string tmp = pReq->postfix;
    map<string, char *>::iterator it = m_typeMap.find(pReq->postfix);
    if (it != m_typeMap.end())
    {
        sprintf(type, "%s", (*it).second);
    }
    return 1;
}

bool CHttps::SSLSendHeader(PREQUEST pReq, BIO *io, string potential_called_method)
{
    char Header[2048] = " ";
    int n = FileExist(pReq);

    if (n) // 请求某文件
    {
        char curTime[50];
        GetCurrentTime(curTime);
        // 取得文件长度
        struct stat buf;
        long length;
        if (stat(pReq->szFileName, &buf) < 0)
        {
            Disconnect(pReq);
            err_exit("Getting filesize error!!\r\n");
        }
        length = buf.st_size;

        // 取得文件的类型
        char ContentType[50] = " ";
        GetContentType(pReq, (char *)ContentType);
        printf("\n[Response]\t\n");
        sprintf((char *)Header,
                "HTTP/1.1 %s\r\nDate: %s\r\nServer: %s\r\nContent-Type: %s\r\nContent-Length: %ld\r\n\r\n",
                HTTP_STATUS_OK,
                curTime,         // Date
                "Villa Server ", // Server"My Https Server"
                ContentType,     // Content-Type
                length);         // Content-length
        printf((char *)Header,
               "HTTP/1.1 %s\r\nDate: %s\r\nServer: %s\r\nContent-Type: %s\r\nContent-Length: %ld\r\n\r\n",
               HTTP_STATUS_OK,
               curTime,         // Date
               "Villa Server ", // Server"My Https Server"
               ContentType,     // Content-Type
               length);         // Content-length
    }
    else if (ALL_METHODS.count(potential_called_method)) // 请求某方法
    {
        char curTime[50];
        GetCurrentTime(curTime);
        sprintf((char *)Header,
                "HTTP/1.1 %s\r\nDate: %s\r\nContent-Type: %s\r\n\r\n",
                HTTP_STATUS_OK,
                curTime,             // Date
                "application/json"); // Content-Type
        printf((char *)Header,
               "HTTP/1.1 %s\r\nDate: %s\r\nContent-Type: %s\r\n\r\n",
               HTTP_STATUS_OK,
               curTime,             // Date
               "application/json"); // Content-Type
    }
    else
    {
        Disconnect(pReq);
        err_exit("The method requested doesn't exist!");
    }

    if (BIO_write(io, Header, strlen(Header)) <= 0) //错误
    {
        return false;
    }
    BIO_flush(io);
    // printf("SSLSendHeader successfully!\n");
    return true;
}

bool CHttps::SSLSendFile(PREQUEST pReq, BIO *io)
{
    int n = FileExist(pReq);
    // 如果请求的文件不存在，则返回
    if (!n)
    {
        Disconnect(pReq);
        err_exit("The file requested doesn't exist!");
    }

    static char buf[2048];
    DWORD dwRead;
    BOOL fRet;
    int flag = 1, nReq;
    // 读写数据直到完成
    while (1)
    {
        // 从file中读入到buffer中
        fRet = read(pReq->hFile, buf, sizeof(buf));
        if (fRet < 0)
        {
            static char szMsg[512];
            sprintf(szMsg, "%s", HTTP_STATUS_SERVERERROR);
            // 向客户端发送出错信息
            if ((nReq = BIO_write(io, szMsg, strlen(szMsg))) <= 0) //错误
            {
                Disconnect(pReq);
                err_exit("BIO_write() error!\n");
            }
            BIO_flush(io);
            break;
        }

        // 完成
        if (fRet == 0)
        {
            // printf("complete \n");
            break;
        }
        // 将buffer内容传送给client
        if (BIO_write(io, buf, fRet) <= 0)
        {
            if (!BIO_should_retry(io))
            {
                printf("BIO_write() error!\r\n");
                break;
            }
        }
        BIO_flush(io);
        //统计发送流量
        pReq->dwSend += fRet;
    }
    // 关闭文件
    if (close(pReq->hFile) == 0)
    {
        pReq->hFile = -1;
        return true;
    }
    else //错误
    {
        Disconnect(pReq);
        err_exit("Closing file error!");
    }
}

bool CHttps::SSLSendJson(PREQUEST pReq, BIO *io)
{
    CHttps *pHttps = (CHttps *)pReq->pHttps;
    const char *buf;
    int length;
    buf = pHttps->_response_json.c_str();
    length = strlen(buf);
    printf("*** SSLSendData !!!\n\t>>>%s<<<\n", buf);
    if (BIO_write(io, buf, length) <= 0)
    {
        if (!BIO_should_retry(io))
        {
            printf("BIO_write() error!\r\n");
        }
    }
    BIO_flush(io);
    pReq->dwSend += length;
}

void CHttps::_groupGenToken_response(str2str &args)
{
    _response_json = "";
    int code = 0;
    string token;
    string message;
    printf("*** loginWithoutToken() !!!\n");

    if (messageList.size() >= MAX_TOKEN_ENTRIES)
    {
        code = -1;
        token = "-1";
        message = "[ERROR] room pool is Full @ loginWithoutToken() !!!";
        printf("%s\n", message.c_str());
    }
    else
    {
        token = to_string(random_6());
        while (messageList.find(token) != messageList.end())
            token = to_string(random_6());
        vector<TextMessage> tmp;
        messageList[token] = tmp;
        message = "Your token is " + token + ", you can use it to invite your partners!";
    }
    char temp_string[2048] = "";
    sprintf((char *)temp_string,
            "{\"code\":%d,\"token\":\"%s\",\"message\":\"%s\"}",
            code,
            token.c_str(),
            message.c_str());
    _response_json = string(temp_string);
}

void CHttps::_groupUseToken_response(str2str &args)
{
    _response_json = "";
    int code = 0;
    string message;
    printf("*** loginWithToken(token) !!!\n");

    if (!args.count("token"))
    {
        code = -1;
        message = "[ERROR] token is None @ loginWithToken(token) !!!";
        printf("%s\n", message.c_str());
    }
    else
    {
        string token = args["token"];
        vector<TextMessage> tmp;
        messageList[token] = tmp;
        message = "Your token is " + token + ", you can use it to invite your partners!";
    }
    char temp_string[2048] = "";
    sprintf((char *)temp_string,
            "{\"code\":%d,\"message\":\"%s\"}",
            code,
            message.c_str());
    _response_json = string(temp_string);
}

void CHttps::_sendText_response(str2str &args)
{
    _response_json = "";
    int code = 0;
    string message;
    printf("*** send(token, name, text, time) !!!\n");

    if (!args.count("token"))
    {
        code = -1;
        message = "[ERROR] token is None @ send(token, ...) !!!";
        printf("%s\n", message.c_str());
    }
    else if (!args.count("name"))
    {
        code = -2;
        message = "[ERROR] name is None @ send(..., name, ...) !!!";
        printf("%s\n", message.c_str());
    }
    else if (!args.count("text"))
    {
        code = -3;
        message = "[ERROR] text is None @ send(..., text, ...) !!!";
        printf("%s\n", message.c_str());
    }
    else if (!args.count("time"))
    {
        code = -4;
        message = "[ERROR] time is None @ send(..., time) !!!";
        printf("%s\n", message.c_str());
    }
    else
    {
        string token = args["token"];
        string name = args["name"];
        string text = args["text"];
        string time = args["time"];
        if (messageList.find(token) != messageList.end())
        {
            TextMessage tmpMessage;
            tmpMessage.name = name;
            tmpMessage.text = text;
            tmpMessage.time = time;
            messageList[token].push_back(tmpMessage);
            message = "You\'ve send the message successful";
        }
        else
        {
            message = "The token you used(" + token + ") is invalid";
            code = -404;
        }
    }
    char temp_string[2048] = "";
    sprintf((char *)temp_string,
            "{\"code\":%d,\"message\":\"%s\"}",
            code,
            message.c_str());
    _response_json = string(temp_string);
}

void CHttps::_recvText_response(str2str &args)
{
    _response_json = "";
    int code = 0;
    string message;
    string dataList;
    printf("*** receive(token) !!!\n");

    if (!args.count("token"))
    {
        code = -1;
        message = "[ERROR] token is None @ receive(token) !!!";
        dataList = "[]";
        printf("%s\n", message.c_str());
    }
    else
    {
        string token = args["token"];
        if (messageList.find(token) == messageList.end())
        {
            message = "The token you used(" + token + ") is invalid";
            code = -404;
            dataList = "[]";
        }
        else
        {
            message = "You are getting messages from room " + args["token"];
            dataList = "[";
            for (auto iter = messageList[token].begin(); iter != messageList[token].end(); iter++)
            {
                string tempData = "{\"name\": \"" + iter->name + "\", \"text\": \"" + iter->text + "\", \"time\": \"" + iter->time + "\"}";
                if (iter + 1 != messageList[token].end())
                    tempData += ",";
                dataList.append(tempData);
            }
            dataList.append("]");
        }
    }
    char temp_string[2048] = "";
    sprintf((char *)temp_string,
            "{\"code\":%d,\"message\":\"%s\",\"data\":%s}",
            code,
            message.c_str(),
            dataList.c_str());
    _response_json = string(temp_string);
}

void printMap(map<string, string> &m)
{
    for (auto ele : m)
        cout << "\t{" << ele.first << ": " << ele.second << "}\n";
}
