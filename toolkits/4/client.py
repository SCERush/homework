import lzma
import os
import socket

def decompress(in_path, out_path):
    lzd = lzma.LZMADecompressor()
    with open(in_path, 'rb') as fin, open(out_path, 'wb') as fout:
        for line in fin:
            decompress_line = lzd.decompress(line)
            fout.write(decompress_line)

def recv():
    data = set()
    while True:
        buffer, _ = sock_recv.recvfrom(BUFFER_SIZE)
        if buffer.startswith(b'over_'):
            fn = buffer[5:].decode()
            for _ in range(5):
                sock_ack.sendto(fn.encode()+b'_ack', address_ack)
            break
        buffer = tuple(buffer.split(b'_', maxsplit=1))
        if buffer not in data:
            data.add(buffer)
        sock_ack.sendto(buffer[0]+b'_ack', address_ack)
    sock_recv.close()
    sock_ack.close()

    data = sorted(data, key=lambda item: int(item[0]))
    with open(rf'{fn}', 'wb') as fp:
        for item in data:
            fp.write(item[1])


if __name__ == '__main__':
    BUFFER_SIZE = 4*1024*1024
    # client address
    client_ip = '192.168.43.135'
    client_port = 8888
    address = (client_ip, client_port)
    sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_recv.bind(address)
    # server address
    server_ip = '192.168.43.132'
    port_ack = 9999
    address_ack = (server_ip, port_ack)
    sock_ack = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # recvie file
    recv()
    
    in_path = 'output.bin.xz'
    out_path = 'output.bin'
    decompress(in_path, out_path)
    os.remove(in_path)
