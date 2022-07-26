import socket
import json
import ast
class SocketClient(object):
    def __init__(self,ip_port):
        self.IP=ip_port
        self.s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.s.connect(ip_port)  # 要连接的IP与端口
    #接收方接受Public
    def RecvPublic(self):
        publicbytes=b""
        while True:  # 循环接收
            try:
                json_string = self.s.recv(1024)
                publicbytes+=json_string
                if len(json_string)<1024:
                    break
            except BlockingIOError as e:
                break
        publicstr=publicbytes.decode()
        publiclist = ast.literal_eval(publicstr)
        return publiclist
    #发送经过加密的Ti和Ui
    def SendTiUi(self,send:list):
        json_string = json.dumps(send)
        self.s.sendto(json_string.encode(), self.IP)
    def Send(self,value):
        self.s.send(str(value).encode())
    def Receivelist(self):

        json_string = self.s.recv(2048)
        jsonstr=json_string.decode()
        jsonlist=ast.literal_eval(jsonstr)
        return jsonlist






