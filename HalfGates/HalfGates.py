import hashlib
import random

#公共变量R---双方约定的
k=8
Rstr = ""
for i in range(k - 1):
    Rstr += str(random.getrandbits(1))
Rstr += '1'
R = int(Rstr, 2)
#pipe
pipe=[]#用来模拟双方通信
flag=False
'''
为AND门生成两个半门
Wa0: 导线a中真值0对应的导线标签,比特串
Wb0: 导线b中真值0对应的导线标签,比特串
R:偏移量, 最低位为1
'''
def GbAnd(Wa0:str,Wb0:str,Wa1:str,Wb1:str,R:int):
    pa=int(Wa0[-1],2)#Wa0的置换标识
    pb=int(Wb0[-1],2)#Wb0的置换标识
    #第一个半门---生成方半门
    TG0=hashlib.sha1(Wa0.encode()).hexdigest()
    TG1=hashlib.sha1(Wa1.encode()).hexdigest()
    TG2=pb and R
    TG=int(TG0,16)^int(TG1,16)^TG2#要传输的乱码表中的一项,生成方半门对应的导线输出标签
    WG0=pa and TG
    WG=int(TG0,16)^WG0#不用发送的那一项，全0
    #第二个半门---求值方半门
    TE0=hashlib.sha1(Wb0.encode()).hexdigest()
    TE1=hashlib.sha1(Wb1.encode()).hexdigest()
    TE2=int(Wa0,2)
    TE=int(TE0,16)^int(TE1,16)^TE2#要传输的乱码表中的一项,求值方半门对应的导线输出标签
    WE0=pb and (TE^int(Wa0,2))
    WE=WE0^int(TE0,16)#不用发送的一项，全0
    #合并半门
    W0=WG^WE
    return W0,TG,TE

#生成导线标签
def GenWireLable(k:int):
    #偏移量
    Wa0=""
    Wb0=""
    for i in range(k):
        Wa0+=str(random.getrandbits(1))
        Wb0+=str(random.getrandbits(1))
    Wa1 = bin(int(Wa0, 2) ^ R)[2:]
    Wb1 = bin(int(Wb0, 2) ^ R)[2:]
    return Wa0,Wb0,Wa1,Wb1

'''
生成乱码表
k:安全参数
Wa0,Wb0,Wa1,Wb1:导线标签
'''
def Gb(R,Wa0,Wb0,Wa1,Wb1):
    #e = [Wa0, Wb0]#用来生成激活标签
    W0,TG,TE=GbAnd(Wa0,Wb0,Wa1,Wb1,R)#W0--输出导线标签
    F=(TG,TE)#乱码表
    #W1=W0^R#输出导线标签--1
    d=int(bin(W0)[-1],2)
    return F,d

'''
获取激活标签
Va:导线的明文值,整型
W0:导线明文值0对应的导线标签,比特串
'''
def GetActiveLable(V:int,W0):
    W0=int(W0,2)
    X=W0^(V and R)#逻辑与,&表示按位与
    return bin(X)[2:]

'''
双方执行OT协议,使得电路生成方获取自己的导线激活标签
这里是模拟OT协议的执行,并不是真正的OT协议,其中W0是Alice的输入,Vb是Bob的输入
与前面的GetActiveLable不同--其输入都是Alice的，尽管他们的功能相同。其中一个写法为：
def OT(Vb,W0):
    Wb=GetActiveLable(Vb,W0)
    return Wb
更好理解的写法在下面
'''
def OT(Vb):
    W=pipe.pop(0)
    if Vb==0:
        return W[0]
    else :
        return W[1]
def pad(S):
    while len(S)<k:
        S='0'+S
    return S
#从乱码表中恢复真值
#电路生成方将自己的导线标签Wa发送给电路求值方
#电路求值方通过OT得到自己的导线标签Wb
#之后电路求值方计算输出导线标签

'''
电路生成方Alice
k: 安全参数
Va:生成方的导线明文值
'''
def Generator(Va):
    if flag:
        res=pipe[0]
        return res
    #1.生成导线标签
    Wa0,Wb0,Wa1,Wb1=GenWireLable(8)
    Wa0=pad(Wa0)
    Wa1=pad(Wa1)
    Wb0=pad(Wb0)
    Wb1=pad(Wb1)
    print("Alice generate the lable of wire a0 is {}".format(Wa0))
    print("Alice generate the lable of wire a1 is {}".format(Wa1))
    print("Alice generate the lable of wire b0 is {}".format(Wb0))
    print("Alice generate the lable of wire b1 is {}".format(Wb1))
    #生成乱码表
    F,d=Gb(R,Wa0,Wb0,Wa1,Wb1)#F是乱码表,d是解密时要用的
    #获取导线激活标签
    Wactive=GetActiveLable(Va,Wa0)
    #将乱码表F,电路生成方导线激活标签,解密信息发送给电路求值方Bob
    pipe.append(F)
    pipe.append(d)
    pipe.append(Wactive)
    #OT协议
    pipe.append((Wb0,Wb1))
    return False

'''
电路求值方Bob
'''
def  Evaluator(Vb):
    #1.获取Alice发来的信息
    F=pipe.pop(0)#乱码表
    d=pipe.pop(0)#解密信息
    Wa=pipe.pop(0)#Alice的激活标签
    Wa=pad(Wa)
    print(f"Bob get the active label of a is {Wa}")
    #2.执行OT协议
    Wb=OT(Vb)
    print(f"Bob get the active label of b is {Wb}")
    #3.计算导线激活标签
    Sa=int(Wa[-1],2)
    Sb=int(Wb[-1],2)
    print(f"Bob get the garbled table from Alice is {F}")
    WGa=int(hashlib.sha1(Wa.encode()).hexdigest(),16)^(Sa and F[0])
    WGb=int(hashlib.sha1(Wb.encode()).hexdigest(),16)^(Sb and (F[1]^int(Wa,2)))
    Wc=WGa^WGb#输出导线标签
    #由输出导线标签得到输出导线明文值
    lsb=int(bin(Wc)[-1],2)
    Vc=d^lsb
    #将导线明文值传递给Alice
    global flag
    if not flag:
        pipe.append(Vc)
        flag=True
    return Vc

if __name__ == '__main__':
    resultA=Generator(1)
    resultB=Evaluator(1)
    result=Generator(0)
    print("the share value is {}".format(resultB))


























