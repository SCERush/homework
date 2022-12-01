#include "common.h"

#include <map>
using namespace std;

typedef map<string, string> str2str;

#define random_6() (rand() % 100000 + 100000)
#define MAX_TOKEN_ENTRIES 99

class CHttps
{
public:
    char *ErrorMsg;                //判断是否初始化过程中出错的消息
    SOCKET m_listenSocket;         //创建监听套接字
    map<string, char *> m_typeMap; // 保存content-type和文件后缀的对应关系map
    HANDLE m_hExit;
    const char *m_strRootDir = "/var/www/html";          // web的根目录
    const char *m_str404html = "/var/www/html/404.html"; // 404界面
    UINT m_nPort;                                        // http server的端口号
    BIO *bio_err;
    static char *pass;
    SSL_CTX *ctx;
    char *initialize_ctx();                         //初始化CTX
    char *load_dh_params(SSL_CTX *ctx, char *file); //加载CTX参数
    static int password_cb(char *buf, int num, int rwflag, void *userdata);

public:
    CHttps(void);
    int TcpListen();
    void err_exit(char *str);

    void StopHttpSrv();  //停止HTTP服务
    bool StartHttpSrv(); //开始HTTP服务

    static void *ListenThread(LPVOID param); //监听线程
    static void *ClientThread(LPVOID param); //客户线程

    bool RecvRequest(PREQUEST pReq, LPBYTE pBuf, DWORD dwBufSize);                //接收HTTP请求
    int Analyze(PREQUEST pReq, LPBYTE pBuf, string &body, string &m, str2str &a); //分析HTTP请求
    void Disconnect(PREQUEST pReq);                                               //断开连接
    void CreateTypeMap();                                                         //创建类型映射
    void SendHeader(PREQUEST pReq);                                               //发送HTTP头
    int FileExist(PREQUEST pReq);                                                 //判断文件是否存在

    void GetCurrentTime(LPSTR lpszString);                        //得到系统当前时间
    bool GetLastModified(HANDLE hFile, LPSTR lpszString);         //得到文件上次修改的时间
    bool GetContentType(PREQUEST pReq, LPSTR type);               //取得文件类型
    void SendFile(PREQUEST pReq);                                 //发送文件
    bool SendBuffer(PREQUEST pReq, LPBYTE pBuf, DWORD dwBufSize); //发送缓冲区内容

public:
    bool SSLRecvRequest(SSL *ssl, BIO *io, LPBYTE pBuf, DWORD dwBufSize, string &o); //接收HTTPS请求
    bool SSLSendHeader(PREQUEST pReq, BIO *io, string method);                       //发送HTTPS头
    bool SSLSendFile(PREQUEST pReq, BIO *io);                                        //由SSL通道发送文件
    bool SSLSendJson(PREQUEST pReq, BIO *io);

private:
    void _groupGenToken_response(str2str &args);
    void _groupUseToken_response(str2str &args);
    void _sendText_response(str2str &args);
    void _recvText_response(str2str &args);
    string _response_json;
    map<string, vector<TextMessage>> messageList; // token --> message list

public:
    ~CHttps(void);
    void Test(PREQUEST pReq);
};

void printMap(map<string, string> &m);