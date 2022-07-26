import hashlib
import random
from Crypto.Util.number import *
import gmpy2
import numpy as np
#OPFR中的接收方R
'''
对于一个OPRF来说：接收方输入r,获得F(r)
对于一个无穷大选一OT来说：在第i个OT协议中接收方选择字符串r,获得H(tj)
'''
def pad(s,k):
    mylist=[]
    while len(s)<k:
        s='0'+s
    for i in range(k):
        mylist.append(int(s[i],2))
    return mylist
def bit_to_int(arr:np.ndarray):
    b=gmpy2.pack(arr.tolist()[::-1],1)
    #b=arr.dot(2**np.arange(arr.size)[::-1])#int
    return b
def int_to_arraybit(num)->np.ndarray:
    r=np.frombuffer((np.binary_repr(num).zfill(128)).encode(), dtype='S1').astype(int)
    return r
class Client(object):
    r:list[bytes]
    k:int
    m:int
    T:np.ndarray
    U:np.ndarray
    def __init__(self,r:list[bytes],k:int):
        #初始化
        self.r=r#OPRF中接收方选择字符串集合
        self.k=k#基础OT协议调用数量
        self.m=len(r)
    '''
    随机预言机，返回一个适当长的随机数
    r:随机数发生器的种子
    k:安全参数32  K=4k=128bit,随机数长度,也就是基础OT协议的数量
    '''
    def C(self,r: bytes):
        hashmd5=hashlib.md5()
        hashmd5.update(r)
        RO = hashmd5.hexdigest()
        RO = int(RO, 16)
        return RO
    '''
    接收方准备两个矩阵
    T:m*K(m行,K列)
    U:m*K(m行,K列)
    '''
    def _GetMatrixTU(self)->np.array:
        Tmatrix = np.random.randint(0,2,[self.m,self.k])
        R=[]
        for i in range(self.m):#行
            tmpr=self.C(self.r[i])
            rlist=int_to_arraybit(tmpr)
            R.append(rlist)
        Rmatrix=np.array(R)
        Umatrix=(Tmatrix+Rmatrix)%2
        return Tmatrix,Umatrix
    #-------------------------#
    #执行基础OT协议
    def OTin(self,public:list):
        n=100583853505936563349958934156069540230937237272164829251910147502682892517403
        #phi=100583853505936563349958934156069540230302714329804675665732665294653644316088
        # e=65537
        # d=48300569963308201247944788696853144034482150886877381446759429169599536754377
        self.T,self.U=self._GetMatrixTU()
        Send=[]
        for i in range(self.k):
            Tint=bit_to_int(self.T[:,i])
            e0=pow(int(Tint),public[i][0],n)
            Uint=bit_to_int(self.U[:,i])
            e1=pow(int(Uint),public[i][1],n)
            Send.append((e0,e1))
        return Send
    @property
    def OPRFout(self)->list:
        outlist=[]
        for i in range(self.m):
            inttj=int(bit_to_int(self.T[i]))
            bytestj=long_to_bytes(inttj)
            hashsha1 = hashlib.sha1()
            hashsha1.update(bytestj)
            out=hashsha1.hexdigest()#bytes or str?
            outlist.append(out)
        return outlist#list[bytes]



















