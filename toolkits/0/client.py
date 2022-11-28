
#coding=utf8
# 客户端
import socket
import os
import hashlib
ip='192.168.80.101'
port=6969


client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  # 生成socket连接对象

client.connect((ip,port))  # 连接
print("服务器已连接")


filename = 'output.bin'
# 1.先接收长度，建议8192
server_response = client.recv(1024)
file_size = int(server_response.decode("utf-8"))
print("接收到的大小：", file_size)

# 2.接收文件内容
client.send("111".encode("utf-8"))  # 接收确认

f = open(filename, "wb")
received_size = 0
m = hashlib.md5()

while received_size < file_size:
    size = 0  # 准确接收数据大小，解决粘包
    if file_size - received_size > 1024: # 多次接收
        size = 1024
    else:  # 最后一次接收完毕
        size = file_size - received_size
    data = client.recv(size)  # 多次接收内容，接收大数据
    data_len = len(data)
    received_size += data_len
    #print("已接收：", int(received_size/file_size*100), "%")
    m.update(data)
    f.write(data)
f.close()
print("实际接收的大小:", received_size)  # 解码
