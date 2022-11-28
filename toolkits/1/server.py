import argparse
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


class State(Enum):
    CLOSED = 0
    LISTEN = 1
    SYN_RCVN = 2
    ESTABLISHED = 3
    CLOSN_WAIT = 4
    LAST_ACK = 5


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


class LFTPserver:
    def __init__(self, server_type, host, port, bufferSize):
        self.server_type = server_type
        self.host = host
        self.port = port
        self.bufferSize = bufferSize
        self.udpServer = socket(AF_INET, SOCK_DGRAM)
        self.udpServer.bind((host, port))
        self.state = State.LISTEN  # 初始状态

        # 用于三次握手
        self.client_isn = -1
        self.server_isn = random.randint(0, 1000)
        self.fileInfo = None

    def start(self):
        if self.server_type == 'data':
            self.handshake()
            if (self.state == State.ESTABLISHED):
                print("客户端传输类型：", self.fileInfo["LFTPType"])
                if self.fileInfo["LFTPType"] == "UPLOAD":
                    self.recvfile()
                elif self.fileInfo["LFTPType"] == "DOWNLOAD":
                    self.sendfile()
            else:
                print("连接建立失败")
            # self.udpServer.close()
            # self.state = State.CLOSED
        elif self.server_type == 'control':
            self.ControlHandShake()

    def ControlHandShake(self):
        self.serverList = []
        self.base_port = 9000
        self.max_port = 9099
        for port in range(self.base_port, self.max_port):
            self.serverList.append(None)
        while True:
            print("等待用户连接传入")
            message, addr = self.udpServer.recvfrom(self.bufferSize)
            print(addr)
            message = LFTPMessage.unpack(message)
            print("getport：", message.getport)
            print(message)
            if message.getport == 1:
                for port in range(self.base_port, self.max_port):
                    if self.serverList[port-self.base_port] == None or self.serverList[port-self.base_port].state == State.CLOSED:
                        print("用户连接传入，分配端口：", port)
                        self.serverList[port-self.base_port] = LFTPserver(
                            server_type='data', host='', port=port, bufferSize=2048)
                        threading.Thread(target=self.ServerRun, args=(
                            self.serverList[port-self.base_port],)).start()
                        content = {"port": port}
                        content = json.dumps(content).encode("utf-8")
                        resp = LFTPMessage(getport=1, content_size=len(
                            content), content=content)
                        self.udpServer.sendto(resp.pack(), addr)
                        break

    def ServerRun(self, server):
        server.start()

    def handshake(self):
        print("等待连接中")
        self.udpServer.settimeout(3)
        while True:
            try:
                message, self.client_addr = self.udpServer.recvfrom(
                    self.bufferSize)
            except Exception as e:
                print("客户连接断开，超时关闭，当前端口：", self.port)
                self.state = State.CLOSED
                break
            message = LFTPMessage.unpack(message)
            if self.state == State.LISTEN:
                if message.SYN == 1:
                    print("收到第一次握手报文", self.client_addr)
                    self.client_isn = message.seqnum
                    res = LFTPMessage(
                        SYN=1, ACK=1, seqnum=self.server_isn, acknum=self.client_isn+1)
                    self.fileInfo = json.loads(
                        message.content[:message.content_size].decode("utf-8"))
                    if self.fileInfo["LFTPType"] == "UPLOAD":
                        res.content = message.content
                    elif self.fileInfo["LFTPType"] == "DOWNLOAD":
                        try:
                            self.fileInfo["filesize"] = os.path.getsize(
                                self.fileInfo["filename"])
                        except Exception as e:
                            print("对应文件已丢失，无法提供下载：",
                                  self.fileInfo["filename"])
                            self.fileInfo["filesize"] = -1
                            res.content = json.dumps(
                                self.fileInfo).encode("utf-8")
                            res.content_size = len(res.content)
                            self.udpServer.sendto(res.pack(), self.client_addr)
                            return
                    res.content = json.dumps(self.fileInfo).encode("utf-8")
                    res.content_size = len(res.content)
                    self.udpServer.sendto(res.pack(), self.client_addr)
                    self.state = State.SYN_RCVN
                    threading.Timer(1, self.handshakeTimer,
                                    [self.state]).start()
                    print("发送第二次握手报文", self.client_addr)
            elif self.state == State.SYN_RCVN:
                if message.SYN == 0 and message.ACK == 1 and message.seqnum == self.client_isn+1 and message.acknum == self.server_isn+1:
                    self.state = State.ESTABLISHED
                    print("收到第三次握手报文", self.client_addr)
                    print("建立连接成功", self.client_addr)
                    break

    def handshakeTimer(self, state):
        if (state == self.state):
            if (state == State.SYN_RCVN):
                print("第二次或第三次握手失败,超时丢包转回LISTEN状态")
                self.state = State.LISTEN   # 超时丢包转回LISTEN状态

    def recvfile(self):
        filename = self.fileInfo["filename"]
        filesize = self.fileInfo["filesize"]

        self.recv_base = 0  # 当前窗口基序号
        self.N = 1000  # 窗口大小
        self.window = []  # 接收方窗口
        for i in range(self.N):
            self.window.append(None)

        recvsize = 0  # 已接收数据大小
        print("开始接收文件 %s" % (filename))
        with open(filename, 'wb') as f:
            # pbar = ProgressBar().start()
            while True:
                try:
                    message, addr = self.udpServer.recvfrom(self.bufferSize)
                except Exception as e:
                    print(self.port, e)
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
                    self.udpServer.sendto(response.pack(), addr)

    def sendfile(self):
        # 握手完毕未进入连接建立状态，退出
        if self.state != State.ESTABLISHED:
            print("连接建立失败")
            self.state = State.CLOSED
            return
        self.cwnd = 1
        self.rwnd = 1000
        self.ssthresh = 8
        self.lock = threading.Lock()
        # 定时器
        self.timer = None
        self.TimeoutInterval = 1
        # 发送窗口
        self.send_window = LFTPSendWindow(0, self.rwnd)
        filename = self.fileInfo["filename"]
        filesize = self.fileInfo["filesize"]

        self.send_buffersize = 1024

        # 应用端持续读取数据填入发送窗口
        with open(filename, 'rb') as f:
            print("开始传送文件:", filename)
            threading.Thread(target=self.recvACK, args=(filesize,)).start()
            while filesize > 0:
                self.lock.acquire()
                if (self.send_window.isFull()):  # 窗口已经满了
                    self.lock.release()
                    time.sleep(0.00001)
                    continue
                if filesize >= self.send_buffersize:
                    content = f.read(self.send_buffersize)  # 每次读出来的文件内容
                    self.send_window.append(content)
                    self.lock.release()
                    filesize -= self.send_buffersize
                else:
                    content = f.read(filesize)  # 最后一次读出来的文件内容
                    self.send_window.append(content)
                    self.lock.release()
                    filesize = 0
                    break

    # 接收客户端ACK，滑动窗口
    def recvACK(self, filesize):

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
        self.udpServer.sendto(first_message.pack(), self.client_addr)
        # 设置超时定时器
        self.timer = threading.Timer(
            self.TimeoutInterval, self.TimeOutAndReSend)
        self.timer.start()

        recvSize = 0
        while (True):
            # 接收信息
            try:
                message = self.udpServer.recv(2048)
            except Exception as e:
                if filesize == recvSize:
                    # pbar.finish()
                    print("服务端接收完毕")
                    self.timer.cancel()
                else:
                    self.timer.cancel()
                    print("超时重连失败")
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
            print("rwnd: ", self.rwnd, ", cwnd: ", self.cwnd)
            # 确认一波
            print(acknum, " ACKTIME: ",
                  self.send_window.getACKTimeBySeqnum(acknum))
            if self.send_window.getACKTimeBySeqnum(acknum) == 4:
                # 三次冗余进行重传，同时更新cwnd和ssthresh
                print("三次冗余", acknum)
                self.ssthresh = self.cwnd/2
                self.cwnd = self.cwnd/2+3
                r_content = self.send_window.getContentBySeqnum(acknum)
                r_message = LFTPMessage(
                    seqnum=acknum, content_size=len(r_content), content=r_content)
                self.udpServer.sendto(r_message.pack(), self.client_addr)
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
                    self.udpServer.sendto(message.pack(), self.client_addr)
                # 重新设置超时定时器
                self.timer.cancel()
                self.timer = threading.Timer(
                    self.TimeoutInterval, self.TimeOutAndReSend)
                self.timer.start()
            elif self.send_window.getACKTimeBySeqnum(acknum) == -1:
                print("服务端接收完毕")
                self.timer.cancel()
                break

            self.lock.release()

            # print(recvSize + "/" + filesize,'\r')
            # pbar.update(int(recvSize/filesize)*100)

            if filesize == recvSize:
                # pbar.finish()
                print("服务端接收完毕")
                self.timer.cancel()
                break

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
        print("超时重传：", seqnum)
        message = LFTPMessage(
            seqnum=seqnum, content_size=len(content), content=content)
        self.udpServer.sendto(message.pack(), self.client_addr)
        self.timer.cancel()
        self.timer = threading.Timer(
            self.timer.interval*2, self.TimeOutAndReSend)
        self.timer.start()


if __name__ == "__main__":
    ip = '192.168.43.132'
    port = 12345
    contrl_server = LFTPserver(
        server_type='control', host=ip, port=port, bufferSize=2048)
    contrl_server.start()
