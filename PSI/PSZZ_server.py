from OPRF import OPRF_server
import Cuckoo_hash
import hashlib
from Crypto.Util.number import *
from OT import OT_client
import numpy as np
import gmpy2
from Communicate import Socket_server
import time
def bin_to_int1(binlist:list[int])->int:
    strint=""
    for _ in binlist:
        strint+=str(_)
    return int(strint,2)
def bit_to_int(arr:np.ndarray):
    b=gmpy2.pack(arr.tolist()[::-1],1)
    return int(b)
class PSZZClient(object):
    def __init__(self,X:list[bytes],S:list[int],socket,StashSize:int):
        self.X=X#输入集合X
        self.n=int(len(X)*1.2)
        self.s=len(X)
        self.S=S#密钥1选择字符串
        self.StashSize=StashSize
        self.socket=socket
    def C(self,r: bytes):
        hashmd5=hashlib.md5()
        hashmd5.update(r)
        RO = hashmd5.hexdigest()
        RO = int(RO, 16)
        return RO
    '''
    获取OPRF输出
    '''
    def OPRF(self):
        OT=OPRF_server.Send(self.S,128,self.X,mysocket)
        Q=OT.GetOTout()
        keys=bit_to_int(np.array(self.S))
        H=[]
        S=['none']
        #计算H集合
        for i in range(len(self.X)):
            for j in range(3):
                hix = Cuckoo_hash.Hash(j, self.X[i], self.n)
                keyq=int(OT_client.bit_to_int(Q[hix]))
                F=keyq^(self.C(self.X[i])&keys)
                encbytes=long_to_bytes(F)
                _sha1 = hashlib.sha1()
                _sha1.update(encbytes)
                H.append(_sha1.hexdigest())
        #计算S集合
        for i in range(len(self.X)):
            for j in range(self.StashSize):
                keyq=int(OT_client.bit_to_int(Q[self.n+j]))
                F=keyq^(self.C(self.X[i])&keys)
                encbytes=long_to_bytes(F)
                _sha1 = hashlib.sha1()
                _sha1.update(encbytes)
                S.append(_sha1.hexdigest())
        return H,S

if __name__=='__main__':
    X=[]#X输入集合
    Xlen=90
    file = open("server.txt",'rb+')#读取文件以字节类型
    for i in range(Xlen):
        text=file.readline().replace(b'\r',b'').replace(b'\n',b'')
        X.append(text)
    file.close()
    S=[]#S选择字符串
    K=128#K个基础OT协议
    for i in range(K):
        S.append(getRandomInteger(1))
    #接收来自client端的stashsize
    mysocket=Socket_server.SocketServer(('127.0.0.1',9999))#生成套接字
    stashsize=mysocket.receive()
    client=PSZZClient(X,S,mysocket,stashsize)
    H,S=client.OPRF()
    #将H和S发送给接收方
    print("Send H to receiver")
    mysocket.sendlist(H)
    time.sleep(0.5)
    print("Send S to receiver")
    mysocket.sendlist(S)
    print("PSZZ protocol at sender has finished!")
















