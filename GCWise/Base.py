import hashlib
import random

k = 64
Rstr = ""
for i in range(k - 1):
    Rstr += str(random.getrandbits(1))
Rstr += '1'
R = int(Rstr, 2)


def pad(S):
    while len(S) < k:
        S = '0' + S
    return S


def GbAnd(Wa0: str, Wb0: str, Wa1: str, Wb1: str, R: int):
    pa = int(Wa0[-1], 2)  # Wa0的置换标识
    pb = int(Wb0[-1], 2)  # Wb0的置换标识
    # 第一个半门---生成方半门
    TG0 = hashlib.sha1(Wa0.encode()).hexdigest()
    TG1 = hashlib.sha1(Wa1.encode()).hexdigest()
    TG2 = pb and R
    TG = int(TG0, 16) ^ int(TG1, 16) ^ TG2  # 要传输的乱码表中的一项,生成方半门对应的导线输出标签
    WG0 = pa and TG
    WG = int(TG0, 16) ^ WG0  # 不用发送的那一项，全0
    # 第二个半门---求值方半门
    TE0 = hashlib.sha1(Wb0.encode()).hexdigest()
    TE1 = hashlib.sha1(Wb1.encode()).hexdigest()
    TE2 = int(Wa0, 2)
    TE = int(TE0, 16) ^ int(TE1, 16) ^ TE2  # 要传输的乱码表中的一项,求值方半门对应的导线输出标签
    WE0 = pb and (TE ^ int(Wa0, 2))
    WE = WE0 ^ int(TE0, 16)  # 不用发送的一项，全0
    # 合并半门
    W0 = WG ^ WE
    return W0, TG, TE


def GenWireLable(k: int, S):
    # 偏移量
    Wa0 = ""
    Wb0 = ""
    random.seed(S)
    for i in range(k):
        Wa0 += str(random.getrandbits(1))
        Wb0 += str(random.getrandbits(1))
    Wa1 = bin(int(Wa0, 2) ^ R)[2:]
    Wb1 = bin(int(Wb0, 2) ^ R)[2:]
    Wa1 = pad(Wa1)
    Wb1 = pad(Wb1)
    random.seed(None)
    return Wa0, Wb0, Wa1, Wb1


def Gb(R, Wa0, Wb0, Wa1, Wb1):
    # e = [Wa0, Wb0]#用来生成激活标签
    W0, TG, TE = GbAnd(Wa0, Wb0, Wa1, Wb1, R)  # W0--输出导线标签
    F = (TG, TE)  # 乱码表

    W1 = W0 ^ R  # 输出导线标签--1
    d = [W0, W1]
    # d0=int(bin(W0)[-1],2)
    return F, d


'''
C：表示电路，构成：[op,输入导线0，输入导线1，输出导线0]
S: 种子
'''


class Base(object):
    def Gb(self, C: list, S):
        # 首先判断种类
        # 异或门---不需要为其生成乱码表，只需要生成导线标签即可
        # 目前每个电路就一个门
        if C == 'XOR':
            Wa0, Wb0, Wa1, Wb1 = GenWireLable(64, S)
            # Wa0和Wb0是随机生成的，Wa1和Wb1是由Wa0和Wb0计算得到的
            # print(f"Wa0: {Wa0}")
            # print(f"Wa1: {Wa1}")
            # print(f"Wb0: {Wb0}")
            # print(f"Wb1: {Wb1}")
            # 但是这样更改，这组标签无法用于AND门的评估
            # _, d = Gb(R, Wa0, Wb0, Wa1, Wb1)
            # Wnew0=d[0]
            # wa0=random.getrandbits(64)
            # wb0=Wnew0^wa0
            # wa1=wa0^R
            # wb1=wb0^R
            # e=[(wa0,wa1),(wb0,wb1)]
            F = [0] * 2
            e = [(int(Wa0, 2), int(Wa1, 2)), (int(Wb0, 2), int(Wb1, 2))]
            W0 = int(Wa0, 2) ^ int(Wb0, 2)
            W1 = W0 ^ R
            d = [W0, W1]
            # print(d)
            # print("------------------------------")
            return F, e, d
        # AND门---需要为其生成乱码表和导线标签
        if C == "AND":
            Wa0, Wb0, Wa1, Wb1 = GenWireLable(64, S)
            # print(f"Wa0: {Wa0}")
            # print(f"Wa1: {Wa1}")
            # print(f"Wb0: {Wb0}")
            # print(f"Wb1: {Wb1}")

            F, d = Gb(R, Wa0, Wb0, Wa1, Wb1)
            e = [(int(Wa0, 2), int(Wa1, 2)), (int(Wb0, 2), int(Wb1, 2))]
            # print(d)
            # print("------------------------------")
            return F, e, d

    def Ev(self, F, X):
        Wa = X[0]
        Wb = X[1]
        if F == [0, 0]:
            return Wa ^ Wb
        Sa = Wa & 1
        Sb = Wb & 1
        # print(f"Wa is {Wa}")
        # print(f"Wb is {Wb}")
        # print(f"Wa is {bin(Wa)[2:]}  {len(bin(Wa)[2:])}")
        # print(f"Wb is {bin(Wb)[2:]}  {len(bin(Wb)[2:])}")
        WA = pad(bin(Wa)[2:])
        # print(WA)
        WB = pad(bin(Wb)[2:])
        # print(WB)
        WGa = int(hashlib.sha1(WA.encode()).hexdigest(), 16) ^ (Sa and F[0])
        WGb = int(hashlib.sha1(WB.encode()).hexdigest(), 16) ^ (Sb and (F[1] ^ Wa))
        Wc = WGa ^ WGb
        # print(f"计算得到的输出标签为: {Wc}")
        return Wc

    def En(self, e, x):
        n = len(e)
        Xlable = []
        for i in range(n):
            (X0, X1) = e[i]
            if x[i] == 0:
                Xlable.append(X0)
            else:
                Xlable.append(X1)
        return Xlable

    def De(self, d, Y):
        m = len(d)
        V = []
        for i in range(m):
            (Y0, Y1) = d[i]
            lsb = int(bin(Y)[-1], 2)
            d0 = int(bin(Y0)[-1], 2)
            Vc = d0 ^ lsb
            V.append(Vc)
        return V
