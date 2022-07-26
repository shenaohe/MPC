from OPRF import OPRF_client
from Cuckoo_hash import CuckooHash
from Communicate import Socket_client
class PSZZClient(object):
    def __init__(self,Y:list[bytes],socket):
        self.Y=Y#输入集合
        self.n=int(len(Y)*1.2)
        self.s=len(Y)
        self.cuckoo = CuckooHash(self.n, self.s)
        self.socket=socket
    '''
    将元素集合Y分散到hash表中
    n:输入集合大小
    Y:输入集合
    s:暂存区大小
    '''
    def dividebox(self):
        self.cuckoo.store(self.Y)
        self.hashtable = self.cuckoo.table
        self.stashtable=self.cuckoo.stash
        self.stashsize = self.cuckoo.StashSize
        self.indexset=self.cuckoo.indexset
    '''
    获取OPRF输出
    '''
    def OPRF(self):
        OT=OPRF_client.Receive(self.hashtable+self.stashtable,self.n+self.s,128,self.socket)#传送的是分好的hash表
        OTout=OT.GetOTout()
        OPRF_Y=[]
        for i in range(len(self.Y)):
            index=self.indexset[i]
            OPRF_Y.append(OTout[index])
        return OPRF_Y

if __name__=='__main__':
    Y=[]#输入集合,即OT协议选择字符串
    Ylen=90
    file = open("client.txt",'rb+')#读取文件以字节类型
    for i in range(Ylen):
        text=file.readline().replace(b'\r',b'').replace(b'\n',b'')
        Y.append(text)
    file.close()
    mysocket = Socket_client.SocketClient(('127.0.0.1', 9999))  # 套接字
    client=PSZZClient(Y,mysocket)
    client.dividebox()
    stashsize=client.stashsize
    #将stashsize发送给client
    mysocket.Send(stashsize)
    OPRFout=client.OPRF()#接收OPRF输出
    stash=client.stashtable#暂存区
    hash=client.hashtable#box
    H=mysocket.RecvPublic()
    print("[+]have received the H from sender")
    S=mysocket.RecvPublic()
    print("[+]have received the S from sender")
    print("-----------------------------------------#################-------------------------------------------------")
    #求交集
    print("Now Receiver is going to seek intersection")
    print(f"[+]Receiver get oprf output from OPRF protocol is {OPRFout}")
    print(f"[+]Receiver get H from OPRF protocol is {H}")
    print(f"[+]Receiver get S from OPRF protocol is {S}")
    intersect=[]
    for i in range(Ylen):
        y=Y[i]
        if y in hash:
            if OPRFout[i] in H:
                intersect.append(y)
        elif y in stash:
            if OPRFout[i] in S:
                intersect.append(y)
    print("get seek intersection:")
    print(intersect)
    print("PSZZ protocol at receiver has finished!")




