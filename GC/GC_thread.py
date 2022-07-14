# 假设只有一个门--异或

import random
import threading
import time
import queue
from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes, bytes_to_long

'''
生成一根导线标签,每一根导线标签有两个
wi=(ki,pi)
ki:标签
pi:置乱标识
'''
def genWireLabel(k):
    ki0 = random.getrandbits(k)
    pi0 = random.getrandbits(1)
    wi0 = (ki0, pi0)
    ki1 = random.getrandbits(k)
    pi1 = 1 - pi0
    wi1 = (ki1, pi1)
    return [wi0, wi1]

'''
门函数:异或门
'''
def G(x1, x2):
    return x1 ^ x2

'''
随机预言机H
A:输入导线标签1（10进制）
B:输入导线标签2（10进制）
'''
def ZeroPadding(data):
    data += b'\x00'
    while len(data) % 16 != 0:
        data += b'\x00'
    return data

def H(A, B, k):
    key = b'1234567812345678'  # AES key 16 bytes
    # 计算K
    mul_a = '0' * (k - 2) + '10'
    A2 = A[0] * int(mul_a, 2) % (2 ** k)
    mul_b = '0' * (k - 3) + '100'
    B4 = B[0] * int(mul_b, 2) % (2 ** k)
    K = bin(A2 ^ B4)[2:]
    T=str(A[1])+str(B[1])
    encrypt = long_to_bytes(int(K + T, 2))
    encrypt = ZeroPadding(encrypt)
    aes = AES.new(key, AES.MODE_ECB)
    cipher = aes.encrypt(encrypt)
    cipher = int(bin(bytes_to_long(cipher))[2:][1:k], 2)
    res = cipher ^ int(K, 2)
    return res

'''
生成乱码表
'''
def genGarbledTable(k):
    #wi标签
    wa=genWireLabel(k)
    wb=genWireLabel(k)
    wc=genWireLabel(k)
    inputv=[(0,0),(0,1),(1,0),(1,1)]
    Enc=[0]*4
    for tuplev in inputv:
        va,vb=tuplev
        A=wa[va]
        B=wb[vb]
        C=wc[G(va,vb)][0]
        e_va_vb=H(A,B,k)^C
        T=int(str(A[1])+str(B[1]),2)
        Enc[T]=e_va_vb
    return Enc,wa,wb,wc

'''
生成解码表
'''
def genDecTable(wc):
    dectable={wc[0]:0,wc[1]:1}
    return dectable

'''
2选1OT协议
'''
def OT2_1(P1,b):
    ab=(1-b)*P1[0][0]+b*P1[1][0]
    if ab==P1[0][0]:
        return P1[0]
    else:
        return P1[1]

#----------------------------------------------#
#模拟协议执行，采用多线程的方式
finalflag=False
class threadAlice(threading.Thread):
    def __init__(self, k, value):
        threading.Thread.__init__(self)
        self.k = k
        self.value = value
    def run(self):
        print("Starting Alice......")
        sender(self.k, self.value)
        print("Exiting Alice......")
class threadBob(threading.Thread):
    def __init__(self, k, value):
        threading.Thread.__init__(self)
        self.k = k
        self.value = value
    def run(self):
        print("Starting Bob......")
        recvder(self.k, self.value)
        print("Exiting Bob......")
#线程处理函数--Alice
def sender(k,truevalue):
    lock.acquire()
    garbledTable, wa, wb, wc = genGarbledTable(k)
    decTable = genDecTable([wc[0][0], wc[1][0]])
    q.put(garbledTable)
    q.put(decTable)
    P1Value = truevalue  # P1的输入值
    P1Lable = wa[P1Value]  # P1的激活标签
    q.put(P1Lable)
    q.put(wb)
    lock.release()
    while 1:#监听Bob
        if finalflag:
            resa=q.get()
            print("Alice get the final output {} from Bob".format(resa))
            break
        time.sleep(1)
#线程处理函数--Bob
def recvder(k,truevalue):
    garbledTable=q.get()
    decTable=q.get()
    P1Lable=q.get()
    #执行OT
    P2Value=truevalue
    q.put(P2Value)
    P2Lable=OT2_1(q.get(),q.get())
    #计算输出的激活标签
    A=P1Lable
    B=P2Lable
    T = int(str(A[1]) + str(B[1]), 2)
    epapb=garbledTable[T]
    wc=H(A,B,k)^epapb
    res=decTable[wc]
    print("Bob get the final output is {},then Bob will send it to Alice".format(res))
    q.put(res)
    global finalflag
    finalflag = True

q=queue.Queue(20)
lock=threading.Lock()
if __name__ == '__main__':
    k = 80
    t1 = threadAlice(k,1)
    t2 = threadBob(k,0)
    t1.start()
    t2.start()
    t1.join()
    t2.join()






