#coding=utf8
# 服务器端

ip="192.168.43.132"
port=6969

import socket
import os
import hashlib
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((ip, port))# 绑定监听端口
server.listen(5)  # 监听
print("监听开始..")

conn, addr = server.accept()

filename = '325513.png'
if os.path.isfile(filename):  # 判断文件存在

    # 1.先发送文件大小，让客户端准备接收
    size = os.stat(filename).st_size  #获取文件大小
    conn.send(str(size).encode("utf-8"))  # 发送数据长度
    print("发送的大小：", size)

    # 2.发送文件内容
    conn.recv(1024)  # 接收确认

    f = open(filename, "rb")
    for line in f:
        conn.send(line)  # 发送数据

    f.close()

    # 3.发送md5值进行校验

server.close()
