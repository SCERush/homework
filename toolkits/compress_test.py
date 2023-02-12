import lzma
import os
import time

import zstandard

filename_in = 'output.bin'
filename_out = 'output.bin.xz'

lzc = lzma.LZMACompressor()
s1 = time.perf_counter()
with open(filename_in, 'rb') as fin, open(filename_out, 'wb') as fout:
    for chunk in fin:
        compressed_chunk = lzc.compress(chunk)
        fout.write(compressed_chunk)
    fout.write(lzc.flush())
e1 = time.perf_counter()
print(e1 - s1)

print(f"Uncompressed size: {os.stat(filename_in).st_size}")

print(f"Compressed size: {os.stat(filename_out).st_size}")


lzd = lzma.LZMADecompressor()
with open(filename_out, 'rb') as fin, open('output', 'wb') as fout:
    for line in fin:
        decompress_line = lzd.decompress(line)
        fout.write(decompress_line)


# 创建LZMAFile实例
s1 = time.perf_counter()
zf = lzma.open('output.bin.xz', mode = 'wb')
data = open('output.bin','rb').read()  # 简化描述未关文件
zf.write(data)  # 写文件
zf.close()  # 关闭
e1 = time.perf_counter()
print(e1 - s1)

s2 = time.perf_counter()
with open('output','wb') as pw:
    zf = lzma.open('output.bin.xz', mode = 'rb') #打开压缩文件
    data=zf.read()  # 解压文件
    pw.write(data)  # 写解压缩文件
    zf.close()
e2 = time.perf_counter()
print(e2 - s2)

# zstd
s3 = time.perf_counter()
cctx = zstandard.ZstdCompressor()
with open('output.bin', "rb") as ifh, open('output.bin.zstd', "wb") as ofh:
    cctx.copy_stream(ifh, ofh)
e3 = time.perf_counter()
print(e3 - s3)

s4 = time.perf_counter()
dctx = zstandard.ZstdDecompressor()
with open('output.bin.zstd', 'rb') as ifh, open('output', 'wb') as ofh:
    dctx.copy_stream(ifh, ofh)
e4 = time.perf_counter()
print(e4 - s4)
