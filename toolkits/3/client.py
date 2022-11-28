import json
import struct
import socket

ip = "192.168.43.132"
port = 9999

buffer = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("192.168.43.133", port))

s.sendto("ok".encode(), (ip, port))
print('Client is ready!')

pack_len, addr = s.recvfrom(4)
head_len = struct.unpack('i', pack_len)[0]
json_head, addr = s.recvfrom(head_len)
json_head = json_head.decode('utf-8')
head = json.loads(json_head)
filesize = head['filesize']
filename = head['filename']

# Recv
count = 0
lost = 0
l = []
rwnd = 32
last_ack = ""
with open('output.bin', 'wb') as f:
    while filesize:
        if filesize >= buffer:
            content, addr = s.recvfrom(buffer + 4)
            filesize -= buffer
            Id, data = struct.unpack('i1024s', content)
            # 收到的包编号不对就舍弃
            if (Id != count):
                lost += 1
                ack = (('ack'+str(count-1)).encode('utf-8'))
                s.sendto(ack, addr)
            # 否则发送正确的ack
            else:
                count += 1
                f.write(data)
                current_ack = (('ack'+str(Id)).encode('utf-8'))
                if (current_ack != last_ack):
                    s.sendto(current_ack, addr)
                last_ack = current_ack
        else:
            content, addr = s.recvfrom(buffer + 4)
            Id, data = struct.unpack('i1024s', content)
            if (Id != count):
                lost += 1
                ack = (('ack'+str(count-1)).encode('utf-8'))
                s.sendto(ack, addr)
            else:
                count += 1
                f.write(data.strip('\0'))
                current_ack = (('ack'+str(Id)).encode('utf-8'))
                if (current_ack != last_ack):
                    s.sendto(current_ack, addr)
                last_ack = current_ack
            print("Socket is closed.")
            exit()
s.close()
