import os
import socket
import sys
import time
from os.path import basename
from threading import Event, Thread

ip = '192.168.43.135'
port = 7777
port_ack = 7778
address = (ip, port)

fn_path = 'output.bin'  # 原始文件名
file_name = [f'{basename(fn_path)}'.encode("utf-8")]

BUFFER_SIZE = 16 * 1024  # 32Kb进行分块处理
positions = []  # 存放每块数据在文件中的起点


def sendto(fn_path):  # 用来发送文件的线程函数
    # 读取文件全部内容
    with open(fn_path, 'rb') as fp:
        content = fp.read()
    # 获取文件大小，做好分块传输
    fn_size = len(content)
    for start in range(fn_size // BUFFER_SIZE + 1):
        positions.append(start * BUFFER_SIZE)
    # 设置事件，启动用来接收确认信息的线程
    e.set()
    # 建立Socket，SOCK_DGRAM表示Socket类型为UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFFER_SIZE)
    # 发送文件数据，直到所有分块都收到确认，否则就不停地发送
    while positions:
        for pos in positions:
            sock.sendto(f'{pos}_'.encode() +
                        content[pos:pos + BUFFER_SIZE], address)
            print("Send pos is: ", pos, "    |", end="\r")
            # time.sleep(0.001)
        print(len(positions), "block remain.        ")
    # 通知其发送成功
    while file_name:
        sock.sendto(b'over_' + file_name[0], address)
    # 关闭套接字
    sock.close()


def recv_ack():  # 用来接收确认信息的线程函数
    # 创建套接字，绑定本地端口，用来接收对方的确认信息
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port_ack))
    # 如果所有分块都确认过，结束循环
    while positions:
        # 预期收到的确认包格式为1234_ack
        data, _ = sock.recvfrom(1024)
        pos = int(data.split(b'_')[0])
        if pos in positions:
            positions.remove(pos)
            print("\t\t\t\t New block in: ", pos, "received.", end="\r")
    # 确认对方收到文件名，并已接收全部数据
    while file_name:
        data, _ = sock.recvfrom(1024)
        fn = data.split(b'_')[0]
        if fn in file_name:
            file_name.remove(fn)
    # 关闭套接字
    sock.close()


t1 = Thread(target=sendto, args=(fn_path,))  # 发送文件线程
t1.start()
e = Event()
e.clear()
e.wait()

t2 = Thread(target=recv_ack)  # 确认线程
t2.start()

# 等待发送线程和接收确认线程都结束
t2.join()
t1.join()
