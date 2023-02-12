import lzma
import socket
from threading import Event, Thread
from time import sleep


def send(file_path):
    with open(file_path, 'rb') as fp:
        content = fp.read()
    _content = lzma.compress(content)
    file_size = len(_content)

    for i in range(file_size//BUFFER_SIZE+1):
        positions.append(i*BUFFER_SIZE)
    e.set()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFFER_SIZE)

    while positions:
        for pos in positions:
            sock.sendto(f'{pos}_'.encode() + _content[pos:pos+BUFFER_SIZE], address)
        sleep(0.1)

    while file_name:
        sock.sendto(b'over_'+file_name[0], address)
    sock.close()


def recv_ack():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(address_ack)

    while positions:
        data, _ = sock.recvfrom(1024)
        pos = int(data.split(b'_')[0])
        if pos in positions:
            positions.remove(pos)

    while file_name:
        data, _ = sock.recvfrom(1024)
        fn = data.split(b'_')[0]
        if fn in file_name:
            file_name.remove(fn)
    sock.close()


if __name__ == '__main__':
    BUFFER_SIZE = 32*1024
    # compress file
    file_path = 'output.bin'
    # server address
    server_ip = '192.168.43.132'
    port_ack = 9999
    address_ack = (server_ip, port_ack)
    # client address
    client_ip = '192.168.43.135'
    client_port = 8888
    address = (client_ip, client_port)
    # storage file block
    positions = []
    file_name = [file_path.encode()]

    # send thread
    t1 = Thread(target=send, args=(file_path,))
    t1.start()
    e = Event()
    e.clear()
    e.wait()
    # ack thread
    t2 = Thread(target=recv_ack)
    t2.start()
    # wait
    t2.join()
    t1.join()
