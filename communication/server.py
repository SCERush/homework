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
from RabinMiller import generateLargePrime, gen_RandNum


class TcpServerSocket(Cmd):
    def __init__(self):
        Cmd.__init__(self)
        self.start_time = ctime()
        print('starting ', self.start_time)
        # DH
        self.p = generateLargePrime()
        self.g = gen_RandNum()
        self.a = gen_RandNum()
        self.p1 = pow(self.g, self.a, self.p)
        self.key = ""
        # RSA
        self.rsa = myRsa.RSA()
        self.e, self.da, self.na = self.rsa.getKey()
        # AES
        self.aes = myAES.AES_CBC()
        self.aesfile = myAES.AES_FILE()

    def conf(self):
        self.host = '127.0.0.1'
        self.port = 21567
        self.buffsize = 1024
        self.addr = (self.host, self.port)

        # 声明一个socket对象 tcpsersocket
        tcpsersock = socket(AF_INET, SOCK_STREAM)
        tcpsersock.bind(self.addr)
        tcpsersock.listen(5)
        print("waiting for connection...")

        self.serversocket, addr = tcpsersock.accept()
        print("client connected from: ", addr)

        # DH exchange key
        print("\nNow, the program is generating the key using the Diffie hellman protocol.")
        # p = generateLargePrime()
        self.serversocket.send(str(self.p).encode('utf-8'))
        # g = gen_RandNum()
        self.serversocket.send(str(self.g).encode('utf-8'))
        print("The big prime number p and rand number g has send to Bob")
        # a = gen_RandNum()
        # p1 = pow(g, a, p)
        self.serversocket.send(str(self.p1).encode('utf-8'))
        p2 = int(self.serversocket.recv(self.buffsize).decode('utf-8'))
        k = pow(p2, self.a, self.p)
        self.key = hashlib.md5(str(k).encode('utf-8')).hexdigest()[8:-8]
        print("Key has been generated : ", self.key, '\n')

        # RSA
        self.serversocket.send(str(self.na).encode('utf-8'))
        self.nb = int(self.serversocket.recv(self.buffsize).decode('utf-8'))

        print("You have sended your RSA public key to Bob and recvied Bob's public key.")
        print("You can communte with Bob now!")
        print("use 'file:' prefix to send a file\n")

    def send(self):
        while 1:
            data = input("input>>")
            if ('file:' in data):
                filepath = data.strip('file:')
                if os.path.isfile(filepath):
                    self.serversocket.send(data.encode('utf-8'))

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
                    self.serversocket.send(fhead)

                    # RSA encrypt md5
                    md5_enc_bytes = hashlib.md5(enc_bytes).hexdigest()
                    # print(type(enc_bytes))
                    enc_md5_bytes = self.rsa.sign(
                        md5_enc_bytes, self.da, self.na)
                    self.serversocket.send(str(enc_md5_bytes).encode('utf-8'))

                    with open(filepath, 'rb') as fp:
                        while True:
                            send_data = fp.read(self.buffsize)
                            if not send_data:
                                break
                            self.serversocket.send(send_data)
                    print("The file has send to client.")
                    os.remove(filepath)

                else:
                    print("File error, please enter again!")
                    continue

            elif (data == ''):
                continue

            else:
                self.serversocket.send("message".encode('utf-8'))

                # AES : str -> base64 str
                enc_text = self.aes.encrypt_message(self.key, data)
                # md5 : base64 str -> md5
                md5_enc_text = hashlib.md5(
                    enc_text.encode('utf-8')).hexdigest()
                # RSA md5 : md5 -> RSA (int)
                enc_md5 = self.rsa.sign(md5_enc_text, self.da, self.na)

                self.serversocket.send(enc_text.encode('utf-8'))
                self.serversocket.send(str(enc_md5).encode('utf-8'))

    def rec(self):
        while 1:
            rdata = self.serversocket.recv(self.buffsize)
            rdata = rdata.decode('utf-8')

            if ('message' in rdata):
                enc_text = self.serversocket.recv(
                    self.buffsize).decode('utf-8')
                enc_md5 = int(self.serversocket.recv(
                    self.buffsize).decode('utf-8'))
                varify = self.rsa.verify(enc_md5, enc_text, self.nb, True)
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
                buf = self.serversocket.recv(fileinfo)

                if buf:
                    filename, filesize = struct.unpack('128sq', buf)
                    fn = filename.strip(str.encode('\00'))
                    fn = fn.strip(str.encode('.en'))
                    new_filename = os.path.join(
                        str.encode('./'), str.encode('recv_') + fn)

                    # recv enc_md5_bytes
                    tmp = self.serversocket.recv(self.buffsize).decode('utf-8')
                    # print(tmp)
                    enc_md5_bytes = int(tmp)

                    # recv enc_bytes
                    recvd_size = 0
                    recvd_data = b''
                    while not recvd_size == filesize:
                        if filesize - recvd_size > self.buffsize:
                            data = self.serversocket.recv(self.buffsize)
                            recvd_size += len(data)
                            recvd_data += data
                        else:
                            data = self.serversocket.recv(
                                filesize - recvd_size)
                            recvd_size = filesize
                            recvd_data += data

                    # verify file
                    # print(type(enc_md5_bytes))
                    varify = self.rsa.verify(
                        enc_md5_bytes, recvd_data, self.nb, False)
                    if (varify == True):

                        with open(new_filename, 'wb') as fp:
                            dec_bytes = self.aesfile.decrypt_file(
                                self.key.encode(), recvd_data)
                            fp.write(dec_bytes)
                        print('\n', ctime(),
                              '\n', "rec file from cli: ", new_filename.decode().strip('./'),
                              '\n', "press enter to continue")

                    else:
                        err = "The key has been leaked and the program is about to be shut down."
                        print(err)
                        sys.exit(1)


def main():
    x = TcpServerSocket()
    x.conf()
    t1 = threading.Thread(target=x.send, name="send")
    t2 = threading.Thread(target=x.rec, name="rec")
    t1.start()
    t2.start()


if __name__ == '__main__':
    main()
