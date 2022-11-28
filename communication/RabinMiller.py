import random


def rabinMiller(num):
    """ RabinMiller算法具体实现 """
    t = num - 1
    s = 0
    # 计算 n - 1 = 2 ^ s * t
    while t % 2 == 0:
        t = t // 2
        s += 1
    for trials in range(10):
        # 随机整数b，2 <= b <= n-2
        b = random.randrange(2, num - 1)
        # r0 = b ^ t(mod n)
        r = pow(b, t, num)
        if r != 1:
            i = 0
            while r != (num - 1):
                if i == s - 1:
                    return False
                else:
                    i = i + 1
                    r = (r ** 2) % num
        return True


def isPrime(num):
    """ 验证素数 """
    if num < 2:
        return False
    lowPrimes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
                 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
                 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241,
                 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349,
                 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449,
                 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569,
                 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661,
                 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787,
                 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907,
                 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997]

    if num in lowPrimes:
        return True
    for prime in lowPrimes:
        if num % prime == 0:
            return False
    return rabinMiller(num)


def generateLargePrime(size=1024):
    """ 生成大素数 """
    while True:
        num = random.randrange(2 ** (size - 1), 2 ** size)
        if isPrime(num):
            return num


def gen_RandNum(size=512):
    """ 512位随机整数 a,b """
    return random.randrange(2 ** (size - 1), 2 ** size)


if __name__ == '__main__':
    import time
    start = time.time()
    print(generateLargePrime(10))
    end = time.time()
    print(end - start)
