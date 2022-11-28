import json
import os
import random
import struct
import sys
import threading
import time
from enum import Enum
from socket import *

# from progressbar import *

sys.path.append("..")


# 表示客户端的状态

class State(Enum):
    CLOSED = 0
    SYN_SEND = 1
    ESTABLISHED = 2
    CLOSN_WAIT = 3
    LAST_ACK = 4


class LFTPMessage:
    def __init__(self, SYN=0, ACK=0, getport=0, seqnum=-1, acknum=-1, rwnd=1000, content_size=0, content=b''):
        self.SYN = SYN
        self.ACK = ACK
        self.getport = getport
        self.seqnum = seqnum  # 序列号
        self.acknum = acknum  # 确认号
        self.rwnd = rwnd
        self.content_size = content_size   # 表示实际的content的大小
        self.content = content  # 二进制表示

    def pack(self):
        return struct.pack("iiiiiii1024s", self.SYN, self.ACK, self.getport, self.seqnum, self.acknum, self.rwnd, self.content_size, self.content)

    @staticmethod
    def unpack(message):
        SYN, ACK, getport, seqnum, acknum, rwnd, content_size, content = struct.unpack(
            "iiiiiii1024s", message)
        return LFTPMessage(SYN, ACK, getport, seqnum, acknum, rwnd, content_size, content)
# 表示发送窗口中的每一项


class SendWindowItem:
    def __init__(self, state, seqnum, content):
        self.state = state  # 0表示可用，1表示已经发送未确认，2表示已经确认
        self.seqnum = seqnum
        self.content = content
        self.acktime = 0  # ack次数(等于4时表示三次冗余)

# 表示发送窗口


class LFTPSendWindow:
    def __init__(self, send_base, rwnd):
        self.window = []
        self.send_base = send_base
        self.nextseqnum = send_base
        self.max = 2000
        self.rwnd = rwnd

    def isFull(self):
        return len(self.window) == self.max

    def isEmpty(self):
        return len(self.window) == 0

    def append(self, content):
        if self.isFull():
            return
        seqnum = self.send_base + len(self.window)
        self.window.append(SendWindowItem(0, seqnum, content))

    def getItemToSend(self):
        if self.nextseqnum < self.send_base + self.rwnd:
            self.window[self.nextseqnum - self.send_base].state = 1  # 变为已经发送状态
            item = self.window[self.nextseqnum - self.send_base]
            self.nextseqnum += 1
            return item
        return None

    # 确认序列号
    def ACKseqnum(self, seqnum):
        if (seqnum >= self.send_base and seqnum < self.send_base + len(self.window)):
            # 因为发回来的acknum等于接收到的seqnum+1
            # 所以其实是确认接收到了acknum-1的包
            if seqnum > self.send_base:
                self.window[seqnum-self.send_base-1].state = 2
            self.window[seqnum-self.send_base].acktime += 1

    def getACKTimeBySeqnum(self, seqnum):
        if (seqnum >= self.send_base and seqnum < self.send_base + len(self.window)):
            return self.window[seqnum-self.send_base].acktime
        # 特殊情况，最后一块到达
        if seqnum == self.send_base + len(self.window):
            return -1
        return 0

    def getContentBySeqnum(self, seqnum):
        if (seqnum >= self.send_base and seqnum < self.send_base + len(self.window)):
            return self.window[seqnum-self.send_base].content
        return None

    def update(self):
        size = 0
        while self.window[0].state == 2:
            size += len(self.window[0].content)
            self.window.pop(0)
            self.send_base += 1
        return size

    def updateSendBase(self, send_base):
        size = 0
        if send_base > self.send_base:
            num = send_base - self.send_base
            for i in range(num):
                size += len(self.window[0].content)
                self.window.pop(0)
            self.send_base = send_base
        return size

    def getSendList(self, cwnd):
        cwnd = min(cwnd, self.rwnd, len(self.window))
        List = []
        while cwnd + self.send_base > self.nextseqnum:
            List.append(self.getItemToSend())
        return List


class LFTPClient:
    def __init__(self, host, port, bufferSize):
        self.host = host
        self.port = port
        self.bufferSize = bufferSize
        self.udpClient = socket(AF_INET, SOCK_DGRAM)
        self.state = State.CLOSED
        self.lock = threading.Lock()
        # 用于三次握手
        self.server_isn = -1
        self.client_isn = random.randint(0, 1000)
        # cwnd
        self.cwnd = 1
        self.rwnd = 1000
        self.ssthresh = 8
        # 定时器
        self.timer = None
        self.TimeoutInterval = 0.01

    # 仅提供一次性服务
    def start(self, LFTPType, filename):
        if LFTPType == "UPLOAD":
            self.ControlHandShake()
            self.UpLoadFile(filename)
        elif LFTPType == "DOWNLOAD":
            self.ControlHandShake()
            self.DownloadFile(filename)
        else:
            print(">>> 输入传输类型错误")

    def ControlHandShake(self):
        con_time = 0
        self.udpClient.settimeout(2)
        while True:
            # 发送请求获取分配端口
            request = LFTPMessage(getport=1)
            request.getport = 1
            self.udpClient.sendto(request.pack(), (self.host, self.port))
            try:
                message = self.udpClient.recv(2048)
            except Exception as e:
                con_time += 1
                if con_time == 10:
                    print("连接失败，网络/服务端故障")
                    return False
                print("连接超时, 重新连接中, 连接次数： ", con_time)
                continue
            message = LFTPMessage.unpack(message)
            if message.getport == 1:
                data = json.loads(
                    message.content[:message.content_size].decode("utf-8"))
                self.port = data["port"]
                return True

    def handshake(self, LFTPType, filename, filesize=0):
        print("开始连接服务器")
        self.fileInfo = {
            "filename": filename,
            "filesize": filesize,
            "LFTPType": LFTPType
        }
        fileInfojson = json.dumps(self.fileInfo).encode("utf-8")
        message = LFTPMessage(SYN=1, seqnum=self.client_isn, content_size=len(
            fileInfojson), content=fileInfojson)

        self.udpClient.sendto(message.pack(), (self.host, self.port))
        self.state = State.SYN_SEND
        threading.Timer(0.2, self.handshakeTimer, [
                        self.state, message, 0]).start()
        print("发送第一次握手报文")

        while True:
            try:
                res = self.udpClient.recv(2048)
            except Exception as e:
                print("接收回应报文超时")
                if self.state == State.CLOSED:
                    print("连接失败")
                    break
                continue
            res = LFTPMessage.unpack(res)
            if self.state == State.SYN_SEND and res.SYN == 1 and res.ACK == 1 and res.acknum == self.client_isn+1:
                print("收到第二次握手响应报文")
                if self.fileInfo["LFTPType"] == "DOWNLOAD":
                    self.fileInfo = json.loads(
                        res.content[:res.content_size].decode("utf-8"))
                    if self.fileInfo["filesize"] == -1:
                        print("文件不存在，无法提供下载：", self.fileInfo["filename"])
                        self.state = State.CLOSED
                        return
                self.server_isn = res.seqnum
                reply_message = LFTPMessage(
                    SYN=0, ACK=1, seqnum=self.client_isn+1, acknum=self.server_isn+1)
                self.udpClient.sendto(
                    reply_message.pack(), (self.host, self.port))
                self.state = State.ESTABLISHED
                print("发送第三次握手报文")
                print("连接建立完毕")
                break

    def handshakeTimer(self, state, message, timeout):
        if (state == self.state):
            if timeout == 10:
                print("第一次握手失败")
                self.state = State.CLOSED
                return
            if (state == State.SYN_SEND):
                self.udpClient.sendto(message.pack(), (self.host, self.port))
                threading.Timer(0.2, self.handshakeTimer, [
                                self.state, message, timeout+1]).start()
                print("第一次握手超时，重新发送第一次握手报文, 当前超时次数：", timeout+1)

    def UpLoadFile(self, filepath):
        try:
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)
        except Exception as e:
            print("文件不存在或打开错误:", filepath)
            return
        # 发起握手建立连接
        self.handshake("UPLOAD", filename, filesize)
        # 握手完毕未进入连接建立状态，退出
        if self.state != State.ESTABLISHED:
            print("连接建立失败，无法上传文件")
            self.state = State.CLOSED
            return

        self.send_window = LFTPSendWindow(0, self.rwnd)

        # 应用端持续读取数据填入发送窗口
        with open(filepath, 'rb') as f:
            print("开始传送文件:", filename)
            threading.Thread(target=self.recvACK, args=(filesize,)).start()
            while filesize > 0:
                if (self.send_window.isFull()):  # 窗口已经满了
                    time.sleep(0.00001)
                    continue
                if filesize >= self.bufferSize:
                    content = f.read(self.bufferSize)  # 每次读出来的文件内容
                    self.lock.acquire()
                    self.send_window.append(content)
                    self.lock.release()
                    filesize -= self.bufferSize
                else:
                    content = f.read(filesize)  # 最后一次读出来的文件内容
                    self.lock.acquire()
                    self.send_window.append(content)
                    self.lock.release()
                    filesize = 0
                    break

    # 接收客户端ACK，滑动窗口
    def recvACK(self, filesize):
        # pbar = ProgressBar().start()

        # 发送第一个数据报文，此时cwnd = 1
        self.cwnd = 1
        while True:
            self.lock.acquire()
            if self.send_window.isEmpty() == False:
                item = self.send_window.getItemToSend()
                if item != None:
                    self.lock.release()
                    break
            self.lock.release()

        first_message = LFTPMessage(seqnum=item.seqnum, content_size=len(
            item.content), content=item.content)
        self.udpClient.sendto(first_message.pack(), (self.host, self.port))
        # 设置超时定时器
        self.timer = threading.Timer(
            self.TimeoutInterval, self.TimeOutAndReSend)
        self.timer.start()

        self.origin_time = time.time()
        self.last_time = time.time()
        self.last_recvsize = 0
        self.compute_result = 0
        self.total_result = 0

        recvSize = 0
        while (True):
            # 接收信息
            try:
                message = self.udpClient.recv(2048)
            except Exception as e:
                if filesize == recvSize:
                    # pbar.finish()
                    print("服务端接收完毕")
                    self.timer.cancel()
                else:
                    print("超时重连失败")
                    self.timer.cancel()
                break
            message = LFTPMessage.unpack(message)
            acknum = message.acknum

            self.lock.acquire()
            # 更新滑动窗口
            if self.cwnd < self.ssthresh:
                self.cwnd += 1
            else:
                self.cwnd += 1/int(self.cwnd)
            # 更新rwnd
            self.send_window.ACKseqnum(acknum)
            self.rwnd = message.rwnd
            self.send_window.rwnd = message.rwnd
            # print("rwnd: ", self.rwnd, ", cwnd: ", self.cwnd)
            #  # 确认一波
            # print(acknum, " ACKTIME: ",self.send_window.getACKTimeBySeqnum(acknum))
            if self.send_window.getACKTimeBySeqnum(acknum) == 4:
                # 三次冗余进行重传，同时更新cwnd和ssthresh
                # print("三次冗余", acknum)
                self.ssthresh = self.cwnd/2
                self.cwnd = self.cwnd/2+3
                r_content = self.send_window.getContentBySeqnum(acknum)
                r_message = LFTPMessage(
                    seqnum=acknum, content_size=len(r_content), content=r_content)
                self.udpClient.sendto(r_message.pack(), (self.host, self.port))
                # 重新设置超时定时器
                self.timer.cancel()
                self.timer = threading.Timer(
                    self.TimeoutInterval, self.TimeOutAndReSend)
                self.timer.start()
            elif self.send_window.getACKTimeBySeqnum(acknum) == 1:
                # 首次接收到，send_base改变
                recvSize += self.send_window.updateSendBase(acknum)
                List = self.send_window.getSendList(self.cwnd)
                for item in List:
                    message = LFTPMessage(seqnum=item.seqnum, content_size=len(
                        item.content), content=item.content)
                    self.udpClient.sendto(
                        message.pack(), (self.host, self.port))
                # 重新设置超时定时器
                self.timer.cancel()
                self.timer = threading.Timer(
                    self.TimeoutInterval, self.TimeOutAndReSend)
                self.timer.start()
            elif self.send_window.getACKTimeBySeqnum(acknum) == -1:
                recvSize = filesize
                self.UpLoadProgress(recvSize, filesize)
                print("服务端接收完毕")
                self.timer.cancel()
                self.lock.release()
                break

            self.lock.release()
            self.UpLoadProgress(recvSize, filesize)
            # pbar.update(int(recvSize/filesize)*100)

            if filesize == recvSize:
                # pbar.finish()
                print("服务端接收完毕")
                self.timer.cancel()
                break

    # 显示下载进度函数
    def DownLoadProgress(self, recvSize, filesize):
        time_change = time.time() - self.last_time
        size_change = recvSize - self.last_recvsize
        if (time_change >= 0.7):
            self.last_time = time.time()
            self.last_recvsize = recvSize
            self.compute_result = size_change/time_change/1024
            self.total_result = recvSize/(time.time()-self.origin_time)/1024
        print('\r%d/%d  已经下载： %d%%  当前下载速度： %d kb/s  平均下载速度： %d kb/s' %
              (recvSize, filesize, int(recvSize/filesize*100), self.compute_result, self.total_result), end='')
        if recvSize == filesize:
            print("")

    # 定时器，超时重传，必定重传的是send_base
    def TimeOutAndReSend(self):
        self.lock.acquire()
        self.ssthresh = self.cwnd/2
        self.cwnd = 1
        seqnum = self.send_window.send_base
        content = self.send_window.getContentBySeqnum(seqnum)
        self.lock.release()
        if content == None:
            return
        # print("超时重传：", seqnum)
        message = LFTPMessage(
            seqnum=seqnum, content_size=len(content), content=content)
        self.udpClient.sendto(message.pack(), (self.host, self.port))
        self.timer.cancel()
        self.timer = threading.Timer(
            self.timer.interval*2, self.TimeOutAndReSend)
        self.timer.start()

    def DownloadFile(self, filename):
        # 发起握手建立连接
        self.handshake("DOWNLOAD", filename)
        # 握手完毕未进入连接建立状态，退出
        if self.state != State.ESTABLISHED:
            print("连接建立失败，无法下载文件")
            self.state = State.CLOSED
            return
        filename = self.fileInfo["filename"]
        filesize = self.fileInfo["filesize"]

        self.recv_base = 0  # 当前窗口基序号
        self.N = 1000  # 窗口大小
        self.window = []  # 接收方窗口
        for i in range(self.N):
            self.window.append(None)

        self.origin_time = time.time()
        self.last_time = time.time()
        self.last_recvsize = 0
        self.compute_result = 0
        self.total_result = 0
        recvsize = 0  # 已接收数据大小

        print("开始接收文件 %s" % (filename))
        with open(filename, 'wb') as f:
            # pbar = ProgressBar().start()
            self.udpClient.settimeout(2)
            while True:
                try:
                    message = self.udpClient.recv(2048)
                except Exception as e:
                    if (recvsize == filesize):
                        # pbar.finish()
                        print("接收完毕，断开连接")
                    else:
                        print("连接已断开")
                    break
                message = LFTPMessage.unpack(message)
                seqnum = message.seqnum
                content = message.content
                content_size = message.content_size
                if (seqnum >= self.recv_base and seqnum < self.recv_base + self.N):
                    self.window[seqnum -
                                self.recv_base] = content[:content_size]
                while self.window[0] != None:
                    f.write(self.window[0])
                    recvsize += len(self.window[0])
                    # pbar.update(int(recvsize / filesize * 100))
                    self.DownLoadProgress(recvsize, filesize)
                    self.window.pop(0)
                    self.window.append(None)
                    self.recv_base += 1

                rwnd = 0
                for item in self.window:
                    if item == None:
                        rwnd += 1
                response = LFTPMessage(
                    ACK=1, seqnum=seqnum, rwnd=rwnd, acknum=self.recv_base)

                if (seqnum <= self.recv_base + self.N):
                    self.udpClient.sendto(
                        response.pack(), (self.host, self.port))

    # 显示上传进度函数
    def UpLoadProgress(self, recvSize, filesize):
        time_change = time.time() - self.last_time
        size_change = recvSize - self.last_recvsize
        if (time_change >= 0.7):
            self.last_time = time.time()
            self.last_recvsize = recvSize
            self.compute_result = size_change/time_change/1024
            self.total_result = recvSize/(time.time()-self.origin_time)/1024
        print('\r%d/%d  已经上传： %d%%  当前上传速度： %d kb/s  平均上传速度： %d kb/s' %
              (recvSize, filesize, int(recvSize/filesize*100), self.compute_result, self.total_result), end='')
        if recvSize == filesize:
            print("")


def getHelp():
    tip = "指令格式：\n" +\
          "  发送文件: LFTP lsend myserver mylargefile\n" +\
          "  下载文件: LFTP lget myserver mylargefile\n" +\
          "参数设置：\n" +\
          "  myserver：url地址或者ip地址\n" +\
          "  mylargefile： 文件路径"
    print('\033[33m%s' % tip)


if __name__ == '__main__':
    # if len(sys.argv) != 5:
    #     getHelp()
    # else:
    #     if sys.argv[1] != "LFTP":
    #         getHelp
    #     else:
    #         if sys.argv[2] == "lsend":
    #             IP = sys.argv[3]
    #             filename = sys.argv[4]
    #             client = LFTPClient(IP, 12345, 1024)
    #             client.start("UPLOAD", filename)
    #         elif sys.argv[2] == "lget":
    #             IP = sys.argv[3]
    #             filename = sys.argv[4]
    #             client = LFTPClient(IP, 12345, 1024)
    #             client.start("DOWNLOAD", filename)
    #         else:
    #             getHelp()

        # client = LFTPClient('127.0.0.1', 12345, 1024)
        # client = LFTPClient('192.168.199.129', 12345, 1024)

    ip = '192.168.43.132'
    port = 12345
    filename = 'output.bin'
    client = LFTPClient(ip, port, 1024)
    client.start("DOWNLOAD", filename)
