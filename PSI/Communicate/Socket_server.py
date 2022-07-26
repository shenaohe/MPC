import socket
import json
import ast
class SocketServer(object):
    def __init__(self,ip_port):
        self.IP=ip_port
        self.s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.s.bind(self.IP)
        self.s.listen(1)
        self.conn,self.address=self.s.accept()
        print(f'server is listening---------->{self.address}')
    def SendPublic(self,Public:list):
        json_string = json.dumps(Public)
        self.conn.sendall(json_string.encode())
    def ReceiveTiUi(self):
        sendbytes=b""
        while True:  # 循环接收
            try:
                json_string = self.conn.recv(1024)
                sendbytes+=json_string
                if len(json_string)<1024:
                    break
            except BlockingIOError as e:
                break
        sendstr=sendbytes.decode()
        sendlist = ast.literal_eval(sendstr)
        return sendlist
    def send(self,value):
        self.s.send(value.encode())
    def sendlist(self,value):
        json_string = json.dumps(value)
        self.conn.sendall(json_string.encode())
    def receive(self):
        client_data = self.conn.recv(2).decode()
        data=int(client_data)
        return data

