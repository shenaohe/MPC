import random
from Crypto.Util.number import long_to_bytes, bytes_to_long
from Crypto.Cipher import AES
import gmpy2


def pad(s):
    l = len(s)
    for i in range(64 - l):
        s = '0' + s
    return s


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


# n---导线数
def GenProjection(n):
    e = []
    for i in range(n):
        X0 = random.getrandbits(64)  # 64bit lable
        X1 = random.getrandbits(64)
        p = random.getrandbits(1)
        label0 = (X0 << 1) + p
        label1 = (X1 << 1) + (p ^ 1)
        e.append((label0, label1))
    return e


# e=GenProjection(4)
# print(e)
def binsplit(x: int):
    bin_ = bin(x)[2:]
    while len(bin_) < 2:
        bin_ = '0' + bin_
    x0 = int(bin_[0], 2)
    x1 = int(bin_[1], 2)
    return x0, x1


class demux(object):
    # 不需要实例化
    def Gb(self, gamma: list, e: list):
        n = 4  # 总输入导线数
        e_all = GenProjection(n)  # 全部的标签
        TruthTable = []
        Garbage0 = []  # 第0个分支的垃圾标签
        Garbage1 = []  # 第1个分支的垃圾标签
        for i in range(n):
            # 每一根线
            line = [(0, 0)] * 4
            lable0, lable1 = e_all[i]
            '''
            标签选择,这里有错误,需要修改
            '''
            x0, x1 = binsplit(i)
            A = gamma[0]
            B = lable0
            e0 = e[0]
            Out = e0[x0][0]
            HashAB = H(A, B)
            e_A_B_0 = HashAB ^ Out
            C1 = random.getrandbits(64)
            e_A_B_1 = HashAB ^ C1
            T = int(str(lsb(A)) + str(lsb(B)), 2)
            line[T] = (e_A_B_0, e_A_B_1)

            A = gamma[0]
            B = lable1
            Out = e0[x0][1]
            HashAB = H(A, B)
            e_A_B_0 = HashAB ^ Out
            e_A_B_1 = HashAB ^ C1

            T = int(str(lsb(A)) + str(lsb(B)), 2)
            line[T] = (e_A_B_0, e_A_B_1)

            A = gamma[1]
            B = lable0
            e1 = e[1]
            C0 = random.getrandbits(64)
            HashAB = H(A, B)
            e_A_B_0 = HashAB ^ C0
            Out = e1[x1][0]
            e_A_B_1 = HashAB ^ Out
            T = int(str(lsb(A)) + str(lsb(B)), 2)
            line[T] = (e_A_B_0, e_A_B_1)

            A = gamma[1]
            B = lable1
            HashAB = H(A, B)
            e_A_B_0 = HashAB ^ C0
            Out = e1[x1][1]
            e_A_B_1 = HashAB ^ Out
            T = int(str(lsb(A)) + str(lsb(B)), 2)
            line[T] = (e_A_B_0, e_A_B_1)

            TruthTable.append(line)
            Garbage0.append(C0)
            Garbage1.append(C1)

        return e_all, TruthTable, Garbage0, Garbage1

    def Ev(self, X: list, gamma, TruthTable, garbage0, garbage1):
        # 按照导线顺序排列输入
        Xr = []
        n = len(garbage0)
        print(f"demux的选择条件标签为：{gamma}")
        print(f"demux的输入标签为：{X}")
        for i in range(n):
            # 第0根导线
            TruthTable0 = TruthTable[i]
            B = X[i]
            A = gamma
            HashAB = H(A, B)
            T = int(str(lsb(A)) + str(lsb(B)), 2)
            epapb = TruthTable0[T]
            for j in range(2):
                W = HashAB ^ epapb[j]
                if W in garbage0:
                    continue
                elif W in garbage1:
                    continue
                elif W not in Xr:
                    Xr.append(W)
        # print(f"+++++计算得到的正确的输出标签为：{Xr}")
        ###先去重
        return Xr
