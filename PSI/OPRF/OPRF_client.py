from Crypto.Util.number import *
import numpy as np
from Cuckoo_hash import CuckooHash
from OT import OT_client
from Communicate import Socket_client
import socket
import time
#OPRF接收方拥有输入Y
class Receive(object):
    def __init__(self,Rset:list[bytes],m:int,K:int,mysocket):
        self.K=K#K个基础协议--默认为128
        self.m=m#m个扩展协议，the m in oprf is 1.2n+s
        self.Y=Rset#在OT中是选择比特串，在OPRF中是经过布谷鸟hash的输入集合Y
        self.socket =mysocket
    def GetOTout(self):
        OTclient=OT_client.Client(self.Y,self.K)
        #接受所有的k个OT协议的公钥
        print("[+]receive Public key from Sender.... start")
        public=self.socket.RecvPublic()
        print("[-]receive Public key from Sender....done")
        #开始传输Ti和Ui
        send=OTclient.OTin(public)
        #传输send--加密后的Ui和Ti给发送方
        print("[+]send Encrypt Ti and Ui to Sender.... start")
        self.socket.SendTiUi(send)
        print("[-]send Encrypt Ti and Ui to Sender.... done")
        #获取OPRF的输出
        OTout=OTclient.OPRFout
        print("******************************************************")
        print("Receiver has finished the OT protocol!")
        return OTout









