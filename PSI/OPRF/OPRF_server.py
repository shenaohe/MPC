from Crypto.Util.number import *
import numpy as np
from Cuckoo_hash import CuckooHash
from OT import OT_server
import json
from Communicate import Socket_server
#OPRF发送方拥有Q矩阵和输入X
class Send(object):
    def __init__(self,S:list[int],K:int,X:list[bytes],socket):
        self.S=S#接收方选择字符串--默认为128位
        self.K=K#基础OT协议的数量
        self.X=X#发送方的输入集合
        self.socket=socket
    def GetOTout(self):
        OTserver=OT_server.server(self.S,self.K)
        public=OTserver.OTsend()#所有公钥对
        #向client端发送k个OT协议所需的所有公钥,只能分批次发送
        print("[+]start to send OT public key to Sender....begin")
        self.socket.SendPublic(public)
        print("[-]finish to send OT public key to Sender....end")
        #接收密文
        print("[+]start to receive OT Encrypt Ti and Ui to Sender....begin")
        send=self.socket.ReceiveTiUi()
        print("[-]finish to receive OT Encrypt Ti and Ui to Sender....end")
        #解密
        print("[+]start to decrypt in OT protocol....begin")
        Q=OTserver.OTout(send)
        print("[-]finish to decrypt in OT protocol....end")
        print("*****************************************************")
        print("Sender has finished the OT protocol!")
        return Q









