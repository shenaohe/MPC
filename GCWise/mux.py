import random
from Crypto.Util.number import long_to_bytes, bytes_to_long
from Crypto.Cipher import AES
import gmpy2


def ZeroPadding(data):
    data += b'\x00'
    while len(data) % 16 != 0:
        data += b'\x00'
    return data


def lsb(X: int):
    return X & 0b1


def H(A, B):
    key = b'1234567812345678'  # AES key 16 bytes
    # 计算K
    mul_a = '0' * (64 - 2) + '10'
    A2 = gmpy2.mod((A >> 1) * int(mul_a, 2), 2 ** 64)
    mul_b = '0' * (64 - 3) + '100'
    B4 = gmpy2.mod((B >> 1) * int(mul_b, 2), 2 ** 64)
    K = bin(A2 ^ B4)[2:]
    T = str(lsb(A)) + str(lsb(B))
    encrypt = long_to_bytes(int(K + T, 2))
    encrypt = ZeroPadding(encrypt)
    aes = AES.new(key, AES.MODE_ECB)
    cipher = aes.encrypt(encrypt)
    cipher = int(bin(bytes_to_long(cipher))[2:][1:64], 2)
    res = cipher ^ int(K, 2)
    return res


def GenProjection(n):
    e = []
    for i in range(n):
        X0 = random.getrandbits(64)  # 16bit lable
        X1 = random.getrandbits(64)
        p = random.getrandbits(1)
        label0 = (X0 << 1) + p
        label1 = (X1 << 1) + (p ^ 1)
        e.append((label0, label1))
    return e


class mux(object):
    def Gb(self, gamma: list, d: list, garbage0, garbage1):
        print(f"输入的gamma为：{gamma}")
        print(f"***mux 用来输入的d为：{d}")
        m = 1  # 总输出导线数
        d_all = GenProjection(m)
        TruthTable = []
        # 第0根输出导线----只有一根总输出导线
        line = [(0, 0)] * 4
        C0lable = d[0][0]
        C1lable = garbage1[0]
        output = d_all[0][0]
        condition = gamma[0]
        Hash = H(condition, C0lable)
        EHash = Hash ^ C1lable ^ output
        T = int(str(lsb(condition)) + str(lsb(C0lable)), 2)
        line[T] = EHash

        C0lable = d[0][1]
        output = d_all[0][1]
        Hash = H(condition, C0lable)
        EHash = Hash ^ C1lable ^ output
        T = int(str(lsb(condition)) + str(lsb(C0lable)), 2)
        line[T] = EHash

        C0lable = garbage0[0]
        C1lable = d[1][0]
        output = d_all[0][0]
        condition = gamma[1]
        Hash = H(condition, C1lable)
        EHash = Hash ^ C0lable ^ output
        T = int(str(lsb(condition)) + str(lsb(C1lable)), 2)
        line[T] = EHash

        C1lable = d[1][1]
        output = d_all[0][1]
        Hash = H(condition, C1lable)
        EHash = Hash ^ C0lable ^ output
        T = int(str(lsb(condition)) + str(lsb(C1lable)), 2)
        line[T] = EHash

        TruthTable.append(line)
        return d_all, TruthTable

    def Ev(self, Truthtable, gamma, Y, garbage, d):
        # print(f"condition is {gamma}")
        # print(f"垃圾输入标签为：{garbage}")
        print(f"***正确输入标签为：{Y}")
        # print(f"乱码表为：{Truthtable}")
        T = int(str(lsb(gamma)) + str(lsb(Y)), 2)
        line = Truthtable[0]
        Ehash = line[T]
        Hash = H(gamma, Y)
        for i in range(2):
            Output = Ehash ^ Hash ^ garbage[i]
            # 判断是否是正确输出
            if Output in d:
                return Output
        return 0
