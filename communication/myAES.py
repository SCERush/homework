import base64
import hashlib
import operator
from Cryptodome.Cipher import AES

AES_BLOCK_SIZE = AES.block_size     # AES 加密数据块大小, 只能是16
AES_KEY_SIZE = 16                   # AES 密钥长度（单位字节），可选 16、24、32，对应 128、192、256 位密钥


def padText(bytes):
    while len(bytes) % AES_BLOCK_SIZE != 0:
        bytes += '\0'.encode()
    return bytes


def padKey(key):
    # 待加密的密钥补齐到对应的位数
    if len(key) > AES_KEY_SIZE:
        return key[:AES_KEY_SIZE]
    while len(key) % AES_KEY_SIZE != 0:
        key += '\0'.encode()
    return key


class AES_CBC:
    # 加密方法
    def encrypt_message(self, key, text):
        key = padKey(key.encode())
        text = padText(text.encode())
        # 偏移量 16个0
        iv = "0000000000000000"
        iv = padText(iv.encode())
        # 初始化加密器
        aes = AES.new(key, AES.MODE_CBC, iv)

        encrypt_aes = aes.encrypt(text)
        # 用base64转成字符串形式
        # 执行加密并转码返回bytes
        encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')
        encrypted_text = encrypted_text.rstrip('\n')
        return encrypted_text

    # 解密方法
    def decrypt_message(self, key, text):
        # 初始化加密器
        key = padKey(key.encode())
        text = text.encode(encoding='utf-8')
        # 偏移量 16个0
        iv = "0000000000000000"
        iv = padKey(iv.encode())
        aes = AES.new(key, AES.MODE_CBC, iv)
        # 优先逆向解密base64成bytes
        base64_decrypted = base64.decodebytes(text)
        # 执行解密密并转码返回str
        decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8')

        PADDING = '\0'
        decrypted_text = decrypted_text.rstrip(PADDING)
        return decrypted_text


class AES_FILE:

    # AES 加密
    def encrypt_file(self, key, bytes):
        key = padKey(key)
        bytes = padText(bytes)
        aes = AES.new(key, AES.MODE_ECB)
        encryptData = aes.encrypt(bytes)
        return encryptData

    # AES 解密
    def decrypt_file(self, key, encryptData):
        key = padKey(key)
        aes = AES.new(key, AES.MODE_ECB)
        bytes = aes.decrypt(encryptData)
        return bytes


if __name__ == '__main__':
    aes = AES_CBC()
    # 加密
    key = "12345678"
    enc_text = aes.encrypt_message(key, "wwww.baidu.com")

    # 解密
    dec_text = aes.decrypt_message(key, enc_text)
    print("key : ", key)
    print("enc_text : ", enc_text)
    print("md5_enc_text : ", hashlib.md5(enc_text.encode('utf-8')).hexdigest())
    print("dec_text : ", dec_text)
    print("md5_dec_text : ", hashlib.md5(dec_text.encode('utf-8')).hexdigest())


    aesfile = AES_FILE()
    with open('275030.jpg', 'rb') as f:
        bytes = f.read()

    encryptBytes = aesfile.encrypt_file(key.encode(), bytes)
    md5_enc_bytes = hashlib.md5(encryptBytes).hexdigest()
    print(md5_enc_bytes)
    decryptBytes = aesfile.decrypt_file(key.encode(), encryptBytes)

    # print(bytes)
    # print(decryptTest)
    with open('275030.en.jpg', 'wb') as f:
        f.write(encryptBytes)

    print("len org file:", len(bytes))
    print("len enc file:", len(encryptBytes))
    print("len dec file:", len(decryptBytes))

    if operator.eq(padText(bytes), decryptBytes) == True:         # 检查加解密是否成功
        print('AES 文件加解密成功！')
    else:
        print('AES 文件加解密失败，解密数据与元数据不相等')
