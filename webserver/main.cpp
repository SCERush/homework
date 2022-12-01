#include "common.h"
#include "https.h"

int main()
{
    CHttps MyHttpObj;
    MyHttpObj.StartHttpSrv();
    while (1)
        sleep(1000);
    return 0;
}