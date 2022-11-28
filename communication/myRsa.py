import base64
import hashlib
import binascii
import operator
from RabinMiller import generateLargePrime


def longToBytes(text):
    """ 将数据转换为int类型 """
    return int(binascii.hexlify(text.encode()), 16)


def bytesToLong(num):
    """ 将int型转换为str类型 """
    return binascii.a2b_hex(str(hex(num)[2::1])).decode()


class RSA:
    def __init__(self) -> None:
        self.e = 65537
        self.p = generateLargePrime()
        self.q = generateLargePrime()
        self.n = self.p * self.q

    def egcd(self, a, b):
        """ 扩展欧几里得算法 """
        if a == 0:
            return b, 0, 1
        else:
            g, y, x = self.egcd(b % a, a)
            return g, x - (b // a) * y, y

    def modinv(self, a, m):
        """ 求乘法逆元 """
        g, x, y = self.egcd(a, m)
        if g != 1:
            raise Exception('modular inverse does not exist')
        else:
            return x % m

    def getKey(self):
        """ 获取公私钥 """
        phi = (self.p - 1) * (self.q - 1)
        d = self.modinv(self.e, phi)
        return self.e, d, self.n

    def verify(self, enc, org, n, type):
        """ 验证函数 """
        enc_m = pow(enc, self.e, n)
        bytes_m = bytesToLong(enc_m)
        if type:
            org_md5 = hashlib.md5(org.encode('utf-8')).hexdigest()
        else:
            org_md5 = hashlib.md5(org).hexdigest()
        return operator.eq(bytes_m, org_md5)

    def sign(self, m, d, n):
        """ 签名函数 """
        bytes_m = longToBytes(m)
        enc_m = pow(bytes_m, d, n)
        return enc_m

    def encrypt(self, m, p, q):
        """ 加密函数 """
        n = p * q
        return pow(m, self.e, n)

    def decrypt(self, c, p, q):
        """ 解密函数 """
        n = p * q
        phi = (p - 1) * (q - 1)
        d = self.modinv(self.e, phi)  # 求私钥d
        return pow(c, d, n)


if __name__ == '__main__':
    p = 9018588066434206377240277162476739271386240173088676526295315163990968347022922841299128274551482926490908399237153883494964743436193853978459947060210411
    q = 7547005673877738257835729760037765213340036696350766324229143613179932145122130685778504062410137043635958208805698698169847293520149572605026492751740223
    m = 8922333133093133239960474404255406756030333
    # print(m)
    rsa = RSA()
    c = rsa.encrypt(m, p, q)
    # print(c)
    d = rsa.decrypt(c, p, q)
    # print(d)

    md5 = "e10adc3949ba59abbe56e057f20f883e"
    d = rsa.modinv(65537, (p-1)*(q-1))
    si = rsa.sign(md5, d, p*q)
    print(si)
    ver = rsa.verify(si, '123456', p*q)
    print(ver)
    # b64si = str(base64.encodebytes(str(si).encode()),encoding='utf-8').rstrip('\n')
    # print(b64si)
    # ver = base64.decodebytes(b64si.encode()).decode()
    # print(ver)
