import os
import sys
import myAES
import myRsa
import struct
import hashlib
import threading
from cmd import Cmd
from socket import *
from time import ctime
from RabinMiller import gen_RandNum


class TcpClientSocket(Cmd):
    def __init__(self, host, port, BUFFSIZE):
        Cmd.__init__(self)
        self.start_time = ctime()
        print('starting ', self.start_time)
        # host
        self.host = host
        self.port = port
        self.buffsize = BUFFSIZE
        self.addr = (self.host, self.port)
        # DH
        self.b = gen_RandNum()
        self.key = ""
        # RSA
        self.rsa = myRsa.RSA()
        self.e, self.db, self.nb = self.rsa.getKey()
        # AES
        self.aes = myAES.AES_CBC()
        self.aesfile = myAES.AES_FILE()

    def conn(self):
        self.clientsocket = socket(AF_INET, SOCK_STREAM)
        self.clientsocket.connect(self.addr)
        print("Success connect the host:", self.host, ":", self.port)

        # DH exchange key
        print("\nNow, the program is generating the key using the Diffie hellman protocol.")
        p = int(self.clientsocket.recv(self.buffsize).decode('utf-8'))
        g = int(self.clientsocket.recv(self.buffsize).decode('utf-8'))
        print("The program has recvied big prime number p and rand number g from Alice")
        # b = gen_RandNum()
        p1 = int(self.clientsocket.recv(self.buffsize).decode('utf-8'))
        p2 = pow(g, self.b, p)
        self.clientsocket.send(str(p2).encode('utf-8'))
        k = pow(p1, self.b, p)
        self.key = hashlib.md5(str(k).encode('utf-8')).hexdigest()[8:-8]
        print("Key has been generated : ", self.key, '\n')

        # RSA
        self.na = int(self.clientsocket.recv(self.buffsize).decode('utf-8'))
        self.clientsocket.send(str(self.nb).encode('utf-8'))

        print(
            "You have sended your RSA public key to Alice and recvied Alice's public key.")
        print("You can communte with Alice now!")
        print("use 'file:' prefix to send a file\n")

    def rec(self):
        while 1:
            rdata = self.clientsocket.recv(self.buffsize)
            rdata = rdata.decode('utf-8')

            if ('message' in rdata):
                enc_text = self.clientsocket.recv(
                    self.buffsize).decode('utf-8')
                tmp = self.clientsocket.recv(self.buffsize).decode('utf-8')
                # print(tmp)
                enc_md5 = int(tmp)

                varify = self.rsa.verify(enc_md5, enc_text, self.na, True)
                if (varify == True):
                    dec_text = self.aes.decrypt_message(self.key, enc_text)
                    print('\n', ctime(),
                          '\n', "rec from ser: ", dec_text,
                          '\n', 'press enter to continue')
                else:
                    err = "The key has been leaked and the program is about to be shut down."
                    print(err)
                    sys.exit(1)

            else:
                fileinfo = struct.calcsize('128sq')
                buf = self.clientsocket.recv(fileinfo)

                if buf:
                    filename, filesize = struct.unpack('128sq', buf)
                    fn = filename.strip(str.encode('\00'))
                    fn = fn.strip(str.encode('.en'))
                    new_filename = os.path.join(
                        str.encode('./'), str.encode('recv_') + fn)

                    # recv enc_md5_bytes
                    tmp = self.clientsocket.recv(self.buffsize).decode('utf-8')
                    # print(tmp)
                    enc_md5_bytes = int(tmp)

                    # recv enc_bytes
                    recvd_size = 0
                    recvd_data = b''
                    while not recvd_size == filesize:
                        if filesize - recvd_size > self.buffsize:
                            data = self.clientsocket.recv(self.buffsize)
                            recvd_size += len(data)
                            recvd_data += data
                        else:
                            data = self.clientsocket.recv(
                                filesize - recvd_size)
                            recvd_size = filesize
                            recvd_data += data

                    # verify file
                    # print(type(enc_md5_bytes))
                    varify = self.rsa.verify(
                        enc_md5_bytes, recvd_data, self.na, False)
                    if (varify == True):

                        with open(new_filename, 'wb') as fp:
                            dec_bytes = self.aesfile.decrypt_file(
                                self.key.encode(), recvd_data)
                            fp.write(dec_bytes)
                        print('\n', ctime(),
                              '\n', "rec file from ser: ", new_filename.decode().strip('./'),
                              '\n', "press enter to continue")

                    else:
                        err = "The key has been leaked and the program is about to be shut down."
                        print(err)
                        sys.exit(1)

    def send(self):
        while 1:
            data = input('send>>')
            if ('file:' in data):
                filepath = data.strip('file:')
                if os.path.isfile(filepath):
                    self.clientsocket.send(data.encode('utf-8'))

                    # encrypt
                    with open(filepath, 'rb') as f:
                        bytes_org = f.read()
                    enc_bytes = self.aesfile.encrypt_file(
                        self.key.encode(), bytes_org)
                    filepath = filepath + '.en'
                    with open(filepath, 'wb') as f:
                        f.write(enc_bytes)

                    # transport
                    fhead = struct.pack('128sq', bytes(os.path.basename(
                        filepath).encode('utf-8')), os.stat(filepath).st_size)
                    self.clientsocket.send(fhead)

                    # RSA encrypt md5
                    md5_enc_bytes = hashlib.md5(enc_bytes).hexdigest()
                    # print(type(enc_bytes))
                    enc_md5_bytes = self.rsa.sign(
                        md5_enc_bytes, self.db, self.nb)
                    self.clientsocket.send(str(enc_md5_bytes).encode('utf-8'))

                    with open(filepath, 'rb') as fp:
                        while True:
                            send_data = fp.read(self.buffsize)
                            if not send_data:
                                break
                            self.clientsocket.send(send_data)
                    print("The file has send to server.")
                    os.remove(filepath)

                else:
                    print("File error, please enter again!")
                    continue

            elif (data == ''):
                continue

            else:
                self.clientsocket.send("message".encode('utf-8'))

                enc_text = self.aes.encrypt_message(self.key, data)
                md5_enc_text = hashlib.md5(
                    enc_text.encode('utf-8')).hexdigest()
                enc_md5 = self.rsa.sign(md5_enc_text, self.db, self.nb)

                self.clientsocket.send(enc_text.encode('utf-8'))
                self.clientsocket.send(str(enc_md5).encode('utf-8'))


def main():
    y = TcpClientSocket('127.0.0.1', 21567, 1024)
    y.conn()
    t1 = threading.Thread(target=y.send, name="send")
    t2 = threading.Thread(target=y.rec, name="rec")
    t1.start()
    t2.start()


if __name__ == '__main__':
    main()
