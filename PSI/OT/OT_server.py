import hashlib
from Crypto.Util.number import *
import numpy as np
#OPRF中的发送方S
def pad(s,k):
    mylist=[]
    while len(s)<k:
        s='0'+s
    for i in range(k):
        mylist.append(int(s[i],2))
    return mylist
def int_to_arraybit(num)->np.ndarray:
    r=np.frombuffer((np.binary_repr(num).zfill(198)).encode(), dtype='S1').astype(int)
    return r
class server(object):
    def __init__(self,s:list,k:int):
        #初始化
        self.s=s#接收方选择字符串
        self.k=k#基础OT协议调用数量
        self._Hash=hashlib.md5()
        self.sk=[]
    def OTsend(self):
        phi = 100583853505936563349958934156069540230302714329804675665732665294653644316088
        pub = []
        for i in range(self.k):
            ski = getPrime(8)
            self.sk.append(ski)
            pk0 = inverse(ski, phi)
            pk1 = getPrime(64)
            if self.s[i] == 0:
                pub.append((pk0, pk1))
            else:
                pub.append((pk1, pk0))
        return pub
    def OTout(self,send):
        n = 100583853505936563349958934156069540230937237272164829251910147502682892517403
        mlist = []
        for i in range(self.k):
            if self.s[i] == 0:
                m = pow(send[i][0], self.sk[i], n)
            else:
                m = pow(send[i][1], self.sk[i], n)
            mlist.append(int_to_arraybit(m))
        marray = np.array(mlist)
        return marray.T#Q矩阵
