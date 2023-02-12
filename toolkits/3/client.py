import os
import socket
import sys
from os.path import basename
from threading import Event, Thread

ip = '192.168.43.132'

port = 7777
port_ack = 7778

BUFFER_SIZE = 32 * 1024
ack_address = (ip, port_ack)

# 用来临时保存数据
data = set()
# 接收数据的socket
sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_recv.bind(('', port))
# 确认反馈地址
sock_ack = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 重复收包次数
repeat = 0

while True:
    buffer, _ = sock_recv.recvfrom(BUFFER_SIZE)
    # 全部接收完成，获取文件名
    if buffer.startswith(b'over_'):  # 匹配开头是否包含特定字符串
        fn = buffer[5:].decode()
        # 多确认几次文件传输结束，防止发送方丢包收不到确认
        for i in range(3):
            sock_ack.sendto(fn.encode()+b'_ack', ack_address)
        break
    # buffer = tuple(buffer.split(b'_',maxsplit = 1))
    buffer = tuple(buffer.split(b'_'))
    if buffer in data:
        repeat = repeat + 1
    else:
        data.add(buffer)
    # print(buffer[0])
    sock_ack.sendto(buffer[0]+b'_ack', ack_address)
sock_recv.close()
sock_ack.close()

data = sorted(data, key=lambda item: int(item[0]))
with open(rf'{fn}', 'wb') as fp:
    for item in data:
        fp.write(item[1])
